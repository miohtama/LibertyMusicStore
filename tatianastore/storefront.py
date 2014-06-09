"""

    Customer visible parts of the store.

"""

import time
import logging
import json
from decimal import Decimal
from django.contrib.auth.decorators import login_required

from django import http
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.conf import settings
from django.template import RequestContext
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.utils.timezone import now
from django.core.cache import cache
from django.utils.translation import ugettext_lazy as _
from django.conf.urls import patterns
from django.conf.urls import url

from . import models
from . import forms

logger = logging.getLogger(__name__)


def index(request):
    """ """
    return render_to_response("about.html", locals(), context_instance=RequestContext(request))


def enter_payment(request):
    """ Ask start entering the payment."""

    admin = request.user.is_authenticated() and request.user.is_staff
    return render_to_response("payment.html", locals(), context_instance=RequestContext(request))


def about(request):
    """ """

    admin = request.user.is_authenticated() and request.user.is_staff
    return render_to_response("about.html", locals(), context_instance=RequestContext(request))


def store(request, slug):
    """ Show artist show inside embed <iframe>.
    """
    store = get_object_or_404(models.Store, slug=slug)
    albums = store.album_set.all()
    songs_without_album = models.Song.objects.filter(store=store, album__isnull=True)
    return render_to_response("storefront/store.html", locals(), context_instance=RequestContext(request))


def order(request, item_type, item_id):
    """ Create an order for the item.

    :param item_type: "album" or "song"

    :param item_id: item id
    """

    albums = songs = []
    if item_type == "album":
        albums = models.Album.objects.filter(id=item_id)
        name = albums[0].name
    elif item_type == "song":
        songs = models.Song.objects.filter(id=item_id)
        name = songs[0].name
    else:
        raise RuntimeError("Bad item type")

    transaction = models.DownloadTransaction.objects.create()

    user_currency = request.COOKIES.get("user_currency")

    transaction.prepare(albums=albums, songs=songs, description=name, ip=request.META["REMOTE_ADDR"], user_currency=user_currency)

    return redirect("pay", str(transaction.uuid))


def pay(request, uuid):
    """ Show order <iframe>.
    """
    transaction = get_object_or_404(models.DownloadTransaction, uuid=uuid)

    if transaction.btc_received_at:
        return redirect("thanks", transaction.uuid)

    converter = models.get_rate_converter()

    if transaction.user_currency and transaction.user_currency != "BTC":
        # The user had chosen specific currency when
        # this transaction was initiated
        user_currency = transaction.user_currency
        user_fiat_amount = converter.convert("BTC", user_currency, transaction.btc_amount)
    else:
        # Default to the store currency
        user_currency = transaction.currency
        user_fiat_amount = transaction.fiat_amount

    if request.method == "POST":
        if "cancel" in request.POST:
            transaction.mark_cancelled()
            return http.HttpResponseRedirect(transaction.store.store_url)

    return render_to_response("storefront/pay.html", locals(), context_instance=RequestContext(request))


def thanks(request, uuid):
    """ Show the download page after the payment.
    """
    transaction = get_object_or_404(models.DownloadTransaction, uuid=uuid)

    if not transaction.btc_received_at:
        return redirect("pay", transaction.uuid)

    # tuples of (name, link)
    download_links = []

    for a in transaction.albums.all():
        download_links.append(dict(name=a.name, link=reverse("download", args=(transaction.uuid,)) + "?album_id=%d" % a.id))
        store = a.store

    for s in transaction.songs.all():
        download_links.append(dict(name=s.name, link=reverse("download", args=(transaction.uuid,)) + "?song_id=%d" % s.id))
        store = s.store

    return render_to_response("storefront/thanks.html", locals(), context_instance=RequestContext(request))


def download(request, uuid):
    """ Download ordered albums/songs. """
    transaction = get_object_or_404(models.DownloadTransaction, uuid=uuid)
    song_id = request.GET.get("song_id")
    album_id = request.GET.get("album_id")

    if album_id:
        album = transaction.albums.get(id=album_id)
        _file = album.download_zip
        download_name = album.name + ".zip"
        content_type = "application/zip"
    elif song_id:
        song = transaction.songs.get(id=song_id)
        _file = song.download_mp3
        content_type = "audio/mp3"
        download_name = song.name + ".mp3"
    else:
        raise RuntimeError("No album or song given for the download")

    response = http.HttpResponse(_file, content_type=content_type)
    response['Content-Disposition'] = 'attachment; filename=%s' % download_name
    return response


def transaction_poll(request, uuid):
    """ Open a long-standing HTTP connection to get transaction info.

    The HTTP response terminates when we get a transaction
    confirmation from the network.
    """

    # print "Entering transaction_poll()"

    transaction = models.DownloadTransaction.objects.get(uuid=uuid)

    redis = cache.raw_client
    pubsub = redis.pubsub()
    pubsub.subscribe("transaction_%s" % transaction.uuid)

    timeout = time.time() + 10

    while time.time() < timeout:
        # print "Transaction polling started %s", now()

        try:
            message = pubsub.get_message()
            if message:
                # print "Got message", message
                if message["type"] != "subscribe":
                    data = json.loads(message["data"])
                    if data["transaction_uuid"] == uuid:
                        return http.HttpResponse(json.dumps(data))
        except Exception as e:
            pubsub.close()
            logger.error("Polling exception")
            logger.exception(e)

        # print "Transaction polling stopped %s", now()
        time.sleep(0.5)

    # print "Returning"
    pubsub.close()
    return http.HttpResponseNotModified()


@login_required
def transaction_past(request):
    customer = request.user.customer
    transactions = customer.transaction_set.all().order_by("-id")
    return render_to_response("transaction_past.html", locals(), context_instance=RequestContext(request))


@login_required
def transaction_check_old(request):
    """ Check all old transaction addresses manually.

    This will catch all blockchain payments we did not get a notification.
    """

    if request.method != "POST":
        return http.HttpResponseRedirect(reverse("transaction_past"))

    from tatianastore import blockchain
    from tatianastore.blockchain import BlockChainAPIError

    customer = request.user.customer
    transactions = customer.transaction_set.all()
    try:
        addresses = blockchain.get_all_address_data()

        checked = succeeded = 0

        for address in addresses:
            try:
                tx = transactions.get(btc_address=address["address"])
            except models.Transaction.DoesNotExist:
                # Already confirmed, different customer, etc.
                continue

            if tx.get_status() != "pending":
                # Cancelled, confirmed, etc.
                continue

            checked += 1

            value = address["total_received"] / Decimal(100000000)

            if tx.check_balance(value, transaction_hash=""):
                succeeded += 1

        messages.success(request, _("Checked %(checked)s pending transactions of which %(succeeded)s had succeeded.") % locals())
        return http.HttpResponseRedirect(reverse("transaction_past"))

    except BlockChainAPIError as e:
        messages.error(request, "BlockChain wallet service error: %s" % e.message)
        return http.HttpResponseRedirect(reverse("transaction_past"))


def profile(request):
    """
    """

    user = request.user

    if request.user.customer:
        return http.HttpResponseRedirect(reverse("enter_payment"))

    return render_to_response("profile.html", locals(), context_instance=RequestContext(request))


urlpatterns = patterns('',
    url(r'^(?P<slug>[-_\w]+)/$', store, name="store"),
    url(r'^order/(?P<item_type>[\w]+)/(?P<item_id>[\d]+)/$', order, name="order"),
    url(r'^pay/(?P<uuid>[^/]+)/$', pay, name="pay"),
    url(r'^transaction_poll/(?P<uuid>[^/]+)/$', transaction_poll, name="transaction_poll"),
    url(r'^thanks/(?P<uuid>[^/]+)/$', thanks, name="thanks"),
    url(r'^download/(?P<uuid>[^/]+)/$', download, name="download"),
)
