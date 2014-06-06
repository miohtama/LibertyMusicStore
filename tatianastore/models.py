import string
from decimal import Decimal
from collections import OrderedDict
import logging
from uuid import uuid4
import random


from django.db import models
from django.utils.encoding import smart_str
from django.contrib.auth import hashers
from django.core.urlresolvers import reverse
from django.db.models import Sum
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager as DjangoUserManager

from easy_thumbnails.fields import ThumbnailerImageField
from autoslug import AutoSlugField

_rate_converter = None

logger = logging.getLogger("__name__")


def get_rate_converter():
    from tatianastore import btcaverage
    global _rate_converter
    if not _rate_converter:
        from django.core.cache import get_cache
        redis = get_cache("default").raw_client
        _rate_converter = btcaverage.RedisConverter(redis)
    return _rate_converter


def filename_gen(basedir):
    """ Generate safe filenames for storage backend """
    def generator(instance, filename):
        salt = hashers.get_hasher().salt()
        salt = smart_str(salt)
        return basedir + salt + u"-" + filename
    return generator


class UserManager(DjangoUserManager):
    pass


class User(AbstractUser):
    """ One user presents artist / store. """

    objects = UserManager()


class Artist(models.Model):
    """ One user presents artist / store. """

    #: Which users can edit data for this artist
    operators = models.ManyToManyField(User, related_name="operated_artits")

    objects = UserManager()

    #: Visible in URls
    slug = AutoSlugField(populate_from='name')

    name = models.CharField(max_length=80, blank=True, null=True)

    #: In which fiat currency the sales of these songs are
    currency = models.CharField(max_length=5, blank=False, null=False, default="USD")

    #: Where this store is hosted (needed for the backlinks)
    store_url = models.URLField()

    def __unicode__(self):
        return u"%s - %s" % (self.slug, self.name)


class Album(models.Model):
    """ Album containing X songs.

    Has cover art. You can buy the whole album with the reduced price.
    """

    #: Visible in URls
    slug = AutoSlugField(populate_from='name')

    name = models.CharField(max_length=80, blank=True, null=True)

    #: Artist's description of this albums
    description = models.TextField(blank=True, null=True)

    owner = models.ForeignKey(Artist)

    cover = ThumbnailerImageField(upload_to=filename_gen("covers/"), blank=True, null=True)

    #: Full album as a zipped file
    download_zip = models.FileField(upload_to=filename_gen("songs/"), blank=False, null=False)

    #: Price in USD
    fiat_price = models.DecimalField(max_digits=16, decimal_places=8, default=Decimal(0))

    def __unicode__(self):
        return u"%s: %s" % (self.owner.name, self.name)

    def get_btc_price(self):
        """ """
        converter = get_rate_converter()
        return converter.convert(self.owner.currency, "BTC", self.fiat_price)


class Song(models.Model):
    """
    """

    #: Owner of the song
    artist = models.ForeignKey(Artist)

    #: Song can belong to album, or exist without an album
    album = models.ForeignKey(Album, null=True)

    #: Song title
    name = models.CharField(max_length=80, blank=True, null=True)

    #: Visible in URls
    slug = AutoSlugField(populate_from='name')

    download_mp3 = models.FileField(upload_to=filename_gen("songs/"), blank=False, null=False)

    prelisten_mp3 = models.FileField(upload_to=filename_gen("prelisten/"), blank=True, null=True)
    prelisten_vorbis = models.FileField(upload_to=filename_gen("prelisten/"), blank=True, null=True)

    #: Song duration in seconds
    duration = models.FloatField(blank=True, null=True)

    #: Price in USD
    fiat_price = models.DecimalField(max_digits=16, decimal_places=8, default=Decimal(0))

    def get_btc_price(self):
        """ """
        converter = get_rate_converter()
        return converter.convert(self.album.owner.currency, "BTC", self.fiat_price)

    def __unicode__(self):
        return u"%s: %s - %s" % (self.album.owner.name, self.album.name, self.name)


class DownloadTransaction(models.Model):
    """ Order to buy some songs, with attached bitcoin transaction info.
    """

    PAYMENT_SOURCE_BLOCKCHAIN = "blockchain.info"
    PAYMENT_SOURCE_BITCOIND = "bitcoind"

    #: Who we notify when the transaction is complete
    customer_email = models.CharField(max_length=64, blank=True, null=True)

    #: Human-readable description of this transaction
    description = models.CharField(max_length=256, editable=False, blank=True, default="")

    uuid = models.CharField(max_length=64, editable=False, blank=True, default=uuid4)

    artist = models.ForeignKey(Artist, null=True)

    albums = models.ManyToManyField(Album, related_name="album_download_transactions")

    songs = models.ManyToManyField(Album, related_name="song_download_transactions")

    created_at = models.DateTimeField(auto_now_add=True)

    #: The currency where the original prices where
    currency = models.CharField(max_length=5, blank=True, null=True)

    #: The currency used to display the prices to the user for this transaction
    user_currency = models.CharField(max_length=5, blank=True, null=True)

    #: The address where the owner must make the payment.
    btc_address = models.CharField(max_length=50, blank=True, null=True)

    # How many BTC was this order
    btc_amount = models.DecimalField(max_digits=16, decimal_places=8, default=Decimal(0))

    #: What's the source price of this transaction
    fiat_amount = models.DecimalField(max_digits=16, decimal_places=8, default=Decimal(0))

    #: Either "blockchain.info" or "bitcoind"
    payment_source = models.CharField(max_length=32, blank=False, null=False)

    btc_received_at = models.DateTimeField(blank=True, null=True)

    #: For manual fixing missing BTC transfers
    manually_confirmed_received_at = models.DateTimeField(blank=True, null=True)

    #: Bitcoin transcation hash which triggered this payment complete
    received_transaction_hash = models.CharField(max_length=256, blank=True, null=True)

    #: The user pressed cancel on the payment page
    cancelled_at = models.DateTimeField(blank=True, null=True)

    #: If we don't receive payment by this time the payment
    #: can be considered as discarded
    expires_at = models.DateTimeField(blank=True, null=True)

    #: When this transaction was discarded
    expired_at = models.DateTimeField(blank=True, null=True)

    # Track where the orders are coming from
    # for the support
    ip = models.IPAddressField(blank=True, null=True)

    def update_new_btc_address(self):
        if self.payment_source == DownloadTransaction.PAYMENT_SOURCE_BLOCKCHAIN:
            self.update_new_btc_address_blockchain()
        else:
            raise RuntimeError("Unknown payment soucre")

    def update_new_btc_address_blockchain(self):
        """ Get blockchain.info payment address for this order.
        """
        from . import blockchain
        label = self.description + u" Total: %s %s Order: %s" % (self.fiat_amount, self.currency, self.uuid)
        self.btc_address = blockchain.create_new_receiving_address(label=label)
        return self.btc_address

    def prepare(self, albums, songs, description, ip):
        """ Prepares this transaction for the payment phase.

        Count order total, initialize BTC addresses, etc.
        """
        self.albums = albums
        self.song = songs
        self.ip = ip
        self.payment_source = DownloadTransaction.PAYMENT_SOURCE_BLOCKCHAIN

        fiat_amount = Decimal(0)

        artist = None
        source_currency = None

        for a in albums:

            # Make sure everything is from the same artist,
            # as currently artist determinates the currency
            if not artist:
                artist = a.artist
            else:
                assert a.artist == artist, "Cannot order cross artists (album)"

            fiat_amount += a.fiat_price
            source_currency = a.artist.currency

        for s in songs:

            # Make sure everything is from the same artist,
            # as currently artist determinates the currency
            if not artist:
                artist = s.artist
            else:
                assert s.artist == artist, "Cannot order cross artists (song)"

            fiat_amount += s.fiat_price
            source_currency = s.artist.currency

        assert source_currency, "Did not get any line items"

        self.artist = artist
        self.currency = source_currency
        self.fiat_amount = fiat_amount

        converter = get_rate_converter()

        self.btc_amount = converter.convert(source_currency, "BTC", fiat_amount)

        self.description = description
        self.update_new_btc_address_blockchain()

        # Make sure we don't accidentally create negative orders
        assert self.btc_amount > 0, "Cannot make empty or negative orders (btc) "
        assert self.fiat_amount > 0, "Cannot make empty or negative orders (fiat)"

        self.save()

    def is_pending(self):
        return self.btc_received_at is None and self.cancelled_at is None

    def is_completed(self):
        return self.btc_received_at is not None

    def is_credited(self):
        return self.fiat_transaction is not None

    def is_cancelled(self):
        return self.cancelled_at is not None

    def get_status(self):
        """ Customer facing status. """
        if self.is_pending():
            return "pending"
        elif self.cancelled_at:
            return "cancelled"
        elif self.manually_confirmed_received_at:
            return "completed (manually marked)"
        elif self.fiat_transaction:
            return "credited"
        else:
            return "completed"

    def mark_manually_confirmed(self):
        """ The user of a customer marks this BTC transaction manually confirmed. """
        self.manually_confirmed_received_at = timezone.now()
        self.btc_received_at = timezone.now()
        self.save()

    def mark_cancelled(self):
        """ The user of a customer marks this BTC transaction manually confirmed. """
        self.cancelled_at = timezone.now()
        self.save()

    def check_balance(self, value, transaction_hash):
        """ Check if this transaction can be confirmed as received.

        :param value: How much value the address of this transaction has now.

        :param transaction_hash: incoming transaction

        :return: True if there was enough balance to confirm this transaction.
        """
        t = self

        assert t.btc_received_at is None
        assert t.cancelled_at is None

        if value >= t.btc_amount - settings.TRANSACTION_BALANCE_CONFIRMATION_THRESHOLD_BTC:
            logger.info("blockhain.info confirmation success, address: %s tx: %s needed: %s got: %s", t.btc_address, transaction_hash, t.btc_amount, value)
            t.received_transaction_hash = transaction_hash
            t.btc_received_at = timezone.now()
            t.save()  # Will trigger signal/Redis pubsub
            return True
        elif value < t.btc_amount - settings.TRANSACTION_BALANCE_CONFIRMATION_THRESHOLD_BTC:
            logger.error("SHORT OF VALUE: Transaction receiving address: %s unconfirmed balance: %s needs: %s", t.btc_address, value, t.btc_amount)
            return False
        elif value == Decimal("0"):
            logger.error("Got notification for the transaction in address %s but unconfimed_balance() still zero", t.btc_address)
            return False
        else:
            raise RuntimeError("Unhandled transaction balance case %s %s %s" % transaction_hash, value, t.btc_address)
