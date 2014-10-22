"""

    Customer visible parts of the store.

"""

import os
import time
import logging
import json
from decimal import Decimal
from django.contrib.auth.decorators import login_required
import datetime

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
from django.views.decorators.csrf import csrf_exempt

import facepy

from . import models
from . import forms
from . import blockchain
from utils import get_session_id

logger = logging.getLogger(__name__)


def store(request, slug):
    """ Show artist show inside embed <iframe>.
    """

    # Force creation of session key
    request.session._get_or_create_session_key()
    request.session["initialized"] = datetime.datetime.now()

    # TODO: Using sessions to manage tracking if we are
    # using iframe inside Facebook or somewhere else causes its problems
    # but it is the cheapest solution to do it now

    # We can get "enter the Facebook iframe mode"
    # as a parameter, besides normal Facebook entry point with a get parameter
    request.session["inside_facebook"] = ("facebook" in request.GET)

    # MArk that the user has succesfully loaded the store from his/her site
    if request.user.is_authenticated():
        for unlikely_user_website_host in ("http://localhost:8000", "https://libertymusicstore"):
            if request.META.get("HTTP_REFERER", "").startswith(unlikely_user_website_host):
                break
        else:
            # Succesfully loaded embed from the user website
            # TODO: Make sure we are the store owner
            wizard = models.WelcomeWizard(request.user)
            wizard.set_step_status("embed_website_store", True)

    store = get_object_or_404(models.Store, slug=slug)
    albums = store.album_set.filter(visible=True)
    songs_without_album = models.Song.objects.filter(store=store, album__isnull=True, visible=True)
    session_id = get_session_id(request)
    content_manager = models.UserPaidContentManager(session_id)
    public_url = settings.PUBLIC_URL
    return render_to_response("storefront/store.html", locals(), context_instance=RequestContext(request))


@csrf_exempt
def facebook(request):
    """ Facebook Page Tab iframe entry point via signed HTTP POST request. """
    signed_request = facepy.SignedRequest.parse(request.POST["signed_request"], settings.FACEBOOK_SECRET_KEY)

    page_id = signed_request["page"]["id"]

    site_url = settings.SITE_URL

    store = models.Store.find_by_facebook_page_id(page_id)
    if not store:
        # Something seriously foobared by Facebook?
        return render_to_response("storefront/facebook_error.html", locals(), context_instance=RequestContext(request))

    # Force creation of session key
    request.session._get_or_create_session_key()
    request.session["initialized"] = datetime.datetime.now()
    request.session["inside_facebook"] = True

    # Mark that the user has succesfully loaded the store from his/her site
    if request.user.is_authenticated():
        # TODO: Make sure we are the store owner
        wizard = models.WelcomeWizard(request.user)
        wizard.set_step_status("embed_facebook_store", True)

    albums = store.album_set.all()
    songs_without_album = models.Song.objects.filter(store=store, album__isnull=True)
    session_id = get_session_id(request)
    content_manager = models.UserPaidContentManager(session_id)
    public_url = settings.PUBLIC_URL

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
        items = albums
    elif item_type == "song":
        songs = models.Song.objects.filter(id=item_id)
        name = songs[0].name
        items = songs
    else:
        raise RuntimeError("Bad item type")

    # Don't allow purchase hidden items
    for item in items:
        if not item.visible:
            raise RuntimeError("Tried purchase non-visible item: %s" % item)

    transaction = models.DownloadTransaction.objects.create()

    user_currency = request.COOKIES.get("user_currency")

    session_id = get_session_id(request)

    transaction.prepare(items, description=name, session_id=session_id, ip=request.META["REMOTE_ADDR"], user_currency=user_currency)

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
            resp = redirect("store", transaction.store.slug)

            # Keep Facebook mode activated
            if request.session.get("inside_facebook"):
                resp['Location'] += '?facebook=true'

            return resp
        logger.error("Received pay() page handling %s %s", request.method, request.POST)

    store = transaction.store

    return render_to_response("storefront/pay.html", locals(), context_instance=RequestContext(request))


def thanks(request, uuid):
    """ Show the download page after the payment.
    """
    transaction = get_object_or_404(models.DownloadTransaction, uuid=uuid)

    if not transaction.btc_received_at:
        return redirect("pay", transaction.uuid)

    # tuples of (name, link)
    download_links = []

    for a in models.DownloadTransactionItem.objects.filter(transaction=transaction):
        content_type, download_name, _file = a.get_download_info()
        url = reverse("download", args=(uuid, a.content_object.uuid, download_name))
        download_links.append(dict(name=a.content_object.name, link=url))

    store = transaction.store

    return render_to_response("storefront/thanks.html", locals(), context_instance=RequestContext(request))


def download(request, transaction_uuid, item_uuid, filename):
    """ Download ordered albums/songs.

    :param: Filename leftover for the browser to pick from URL, see http://stackoverflow.com/a/1365186/315168
    """
    transaction = get_object_or_404(models.DownloadTransaction, uuid=transaction_uuid)

    items = models.DownloadTransactionItem.objects.filter(transaction=transaction)

    for item in items:
        if item.content_object.uuid == item_uuid:
            break
    else:
        return http.HttpResponseNotFound("This download did not contain the mentioned item")

    content_type, download_name, _file = item.get_download_info()

    response = http.HttpResponse(_file, content_type=content_type)
    response['Content-Disposition'] = 'attachment'
    response['Content-Length'] = _file.size
    return response


def embed(request, slug):
    """ Return JavaScript source needed to embed this store. """
    store = get_object_or_404(models.Store, slug=slug)
    store_url = reverse("store", args=(store.slug,))
    public_url = settings.PUBLIC_URL
    return render_to_response("storefront/embed.js", locals(), context_instance=RequestContext(request), content_type="text/javascript")


def embed_code(request, slug):
    """ View embed example code. """
    store = get_object_or_404(models.Store, slug=slug)
    public_url = settings.PUBLIC_URL
    embed_src = request.build_absolute_uri(reverse("embed", args=(store.slug,)))
    return render_to_response("storefront/embed_code.html", locals(), context_instance=RequestContext(request))


@login_required
def embed_preview(request, slug):
    """ View the preview of the store """
    store = get_object_or_404(models.Store, slug=slug)
    public_url = settings.PUBLIC_URL
    embed_src = request.build_absolute_uri(reverse("embed", args=(store.slug,)))

    # The user managed to preview their store
    wizard = models.WelcomeWizard(request.user)
    wizard.set_step_status("preview_store", True)

    return render_to_response("storefront/embed_preview.html", locals(), context_instance=RequestContext(request))


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

    # At the beginning of the poll do force one manual refresh of the address.
    # This way we mitigate problems with unreliable BlochChain notifications
    # and unreliable Redis pubsub
    if blockchain.force_check_old_address(transaction):
        return http.HttpResponse(json.dumps(transaction.get_notification_message()))

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


urlpatterns = patterns('',
    url(r'^facebook/$', facebook, name="facebook"),
    url(r'^(?P<slug>[-_\w]+)/embed/$', embed, name="embed"),
    url(r'^(?P<slug>[-_\w]+)/embed-code/$', embed_code, name="embed_code"),
    url(r'^(?P<slug>[-_\w]+)/embed-preview/$', embed_preview, name="embed_preview"),
    url(r'^(?P<slug>[-_\w]+)/$', store, name="store"),
    url(r'^order/(?P<item_type>[\w]+)/(?P<item_id>[\d]+)/$', order, name="order"),
    url(r'^pay/(?P<uuid>[^/]+)/$', pay, name="pay"),
    url(r'^transaction_poll/(?P<uuid>[^/]+)/$', transaction_poll, name="transaction_poll"),
    url(r'^thanks/(?P<uuid>[^/]+)/$', thanks, name="thanks"),
    url(r'^download/(?P<transaction_uuid>[^/]+)/(?P<item_uuid>[^/]+)/(?P<filename>[^/]+)$', download, name="download"),
)
