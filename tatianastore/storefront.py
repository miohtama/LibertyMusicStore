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


def artist(request, slug):
    """ Show artist show inside embed <iframe>.
    """
    artist = get_object_or_404(models.Artist, slug=slug)
    albums = artist.album_set.all()
    songs_without_album = models.Song.objects.filter(artist=artist, album__isnull=True)
    return render_to_response("storefront/artist.html", locals(), context_instance=RequestContext(request))


def order(request, item_type, item_id):
    """ Create an order for the item.

    :param item_type: "album" or "song"

    :param item_id: item id
    """

    albums = songs = []
    if item_type == "album":
        albums = models.Album.objects.filter(id=item_id)
        name = albums[0].name
    else:
        songs = models.Song.objects.filter(id=item_id)
        name = songs[0].name

    transaction = models.DownloadTransaction.objects.create()

    transaction.prepare(albums=albums, songs=songs, description=name, ip=request.META["REMOTE_ADDR"])

    return redirect("pay", str(transaction.uuid))


def pay(request, uuid):
    """ Show order <iframe>.
    """
    transaction = get_object_or_404(models.DownloadTransaction, uuid=uuid)

    if request.method == "POST":
        if "cancel" in request.POST:
            transaction.mark_cancelled()
            return http.HttpResponseRedirect(transaction.artist.store_url)

    return render_to_response("storefront/pay.html", locals(), context_instance=RequestContext(request))


def download_song(request, transaction_uuid, song_slug):
    """ Download ordered songs. """
    transaction = models.Transaction.objects.get(uuid=transaction_uuid)

    if request.user.customer and transaction.customer == request.user.customer:
        if transaction.is_pending():
            return http.HttpResponseRedirect(reverse("transaction_wait", args=(uuid,)))

    return http.HttpResponseRedirect(reverse("transaction_info", args=(uuid,)))


def transaction_wait(request, uuid):
    """ """
    transaction = models.Transaction.objects.get(uuid=uuid)

    if transaction.get_status() != "pending":
        # Wait page can be only opened when the transaction is pending
        return http.HttpResponseRedirect(reverse("transaction", args=(transaction.uuid,)))

    admin = request.user.is_authenticated() and request.user.is_staff
    return render_to_response("transaction_wait.html", locals(), context_instance=RequestContext(request))


def transaction_actions(request, uuid):
    """ Show a past transaction info."""
    transaction = models.Transaction.objects.get(uuid=uuid)

    if request.method != "POST":
        return http.HttpResponseRedirect(reverse("transaction", args=(transaction.uuid,)))

    if "transaction-cancel" in request.POST:
        transaction.cancelled_at = now()
        transaction.save()
        return http.HttpResponseRedirect(reverse("transaction", args=(transaction.uuid,)))

    if "transaction-confirm-manually" in request.POST:
        transaction.mark_manually_confirmed()
        return http.HttpResponseRedirect(reverse("transaction", args=(transaction.uuid,)))


def transaction_info(request, uuid):
    """ Show a past transaction info."""
    transaction = models.Transaction.objects.get(uuid=uuid)
    admin = request.user.is_authenticated() and request.user.is_staff
    return render_to_response("transaction_info.html", locals(), context_instance=RequestContext(request))


def transaction_poll(request, uuid):
    """ Open a long-standing HTTP connection to get transaction info.

    The HTTP response terminates when we get a transaction
    confirmation from the network.
    """

    print "Entering transaction_poll()"

    transaction = models.Transaction.objects.get(uuid=uuid)

    customer = transaction.customer

    redis = cache.raw_client
    pubsub = redis.pubsub()
    pubsub.subscribe("customer_%d" % customer.id)

    timeout = time.time() + 10

    while time.time() < timeout:
        print "Transaction polling started %s", now()

        try:
            message = pubsub.get_message()
            if message:
                print "Got message", message
                if message["type"] != "subscribe":
                    data = json.loads(message["data"])
                    if data["transaction_uuid"] == uuid:
                        return http.HttpResponse(json.dumps(data))
        except Exception as e:
            pubsub.close()
            logger.error("Polling exception")
            logger.exception(e)

        print "Transaction polling stopped %s", now()
        time.sleep(0.5)

    print "Returning"
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
    url(r'^(?P<slug>[-_\w]+)/$', artist, name="artist"),
    url(r'^order/(?P<item_type>[\w]+)/(?P<item_id>[\d]+)/$', order, name="order"),
    url(r'^pay/(?P<uuid>[^/]+)/$', pay, name="pay"),
    url(r'^thanks/(?P<uuid>[^/]+)/$', pay, name="thanks"),
)
