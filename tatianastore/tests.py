# -*- coding: utf-8 -*-
"""


"""
from decimal import Decimal
import datetime
import random
import os

from mock import patch

from django.utils import timezone
from django.test import TestCase
from django.conf import settings
from django.core.cache import get_cache

from . import models
from . import tasks
from . import zipupload
from . import blockchain
from . import signup
from . import creditor

# Don't accidentally allow to run against the production Redis
assert settings.CACHES["default"]["LOCATION"] == "127.0.0.1:6379:10", "Don't run against production Redis"


def clear():
    models.Store.objects.all().delete()
    models.Album.objects.all().delete()
    models.Song.objects.all().delete()
    models.User.objects.all().delete()

    redis = get_cache("default")
    redis.clear()


class DownloadTransactionTestCase(TestCase):
    """ Test that we can create and retrieve download transactions.. """

    def setUp(self):
        models.DownloadTransaction.objects.all().delete()

        test_store = models.Store.objects.create(name="Test Store")
        test_store.currency = settings.DEFAULT_PRICING_CURRENCY
        test_store.store_url = "http://localhost:8000/store/test-store/"
        test_store.save()

        test_album = models.Album.objects.create(name="Test Album", store=test_store)
        test_album.fiat_price = Decimal("8.90")
        test_album.description = u"My very first album åäö"
        test_album.save()

        test_song1 = models.Song.objects.create(name="Song A", album=test_album, store=test_store)
        test_song1.fiat_price = Decimal("0.95")
        test_song1.save()

        self.test_store = test_store
        self.test_album = test_album
        self.test_song = test_song1

        redis = get_cache("default")
        redis.clear()

        tasks.update_exchange_rates()

    def test_pay_song_and_album(self):
        """ Check that we can download songs after the tranaction has been paid. """

        session_id = "123"

        transaction = models.DownloadTransaction.objects.create()
        user_currency = settings.DEFAULT_PRICING_CURRENCY
        items = [self.test_album, self.test_song]
        transaction.prepare(items, description="Test download", session_id=session_id, ip="1.1.1.1", user_currency=user_currency)

        transaction.mark_payment_received()

        content_manager = models.UserPaidContentManager(session_id)
        self.assertTrue(content_manager.has_item(self.test_song))
        self.assertTrue(content_manager.has_item(self.test_album))


class UploadAlbumTestCase(TestCase):
    """ Test album uploads as zip. """

    def setUp(self):
        clear()
        self.test_store = test_store = models.Store.objects.create(name="Test Store")
        test_store.currency = "USD"
        test_store.store_url = "http://localhost:8000/store/test-store/"
        test_store.save()

    def test_upload_zip(self):
        test_zip = os.path.join(os.path.dirname(__file__), "static", "testdata", "test_album_åäö.zip")

        test_zip = open(test_zip, "rb")

        zipupload.upload_album(self.test_store, "Test Album",  test_zip, Decimal("9.90"), Decimal("1.0"))

        # Check that all extracted content is downloadable on the disk
        self.assertEqual(2, models.Song.objects.all().count())
        for s in models.Song.objects.all():
            self.assertTrue(os.path.exists(os.path.join(settings.MEDIA_ROOT, s.download_mp3.name)), "MP3 Does not exist %s" % s.download_mp3.name)
            self.assertTrue(os.path.exists(os.path.join(settings.MEDIA_ROOT, s.prelisten_mp3.name)))

        a = models.Album.objects.first()
        self.assertTrue(os.path.exists(os.path.join(settings.MEDIA_ROOT, a.download_zip.name)))
        self.assertTrue(os.path.exists(os.path.join(settings.MEDIA_ROOT, a.cover.name)))

        s = models.Song.objects.all()[0]
        self.assertEqual(u'Title åäö', s.name)

        s = models.Song.objects.all()[1]
        self.assertEqual(u'Title 2', s.name)


class CreditTransactionTestCase(TestCase):
    """ See that the store owner receives the payment. """

    def setUp(self):

        clear()

        owner = models.User.objects.create(username="foobar", email="foobar@example.com")

        self.test_store = test_store = models.Store.objects.create(name=u"Test Store åäö")
        test_store.currency = settings.DEFAULT_PRICING_CURRENCY
        test_store.store_url = "http://localhost:8000/store/test-store/"
        test_store.operators = [owner]
        test_store.btc_address = "19356KxTs9Bw5AAdxens5hoxDSp5bsUKse"
        test_store.save()

        test_song1 = models.Song.objects.create(name="Song A", store=test_store)
        test_song1.fiat_price = Decimal("0.01")
        test_song1.save()

        self.test_store = test_store
        self.test_song = test_song1

        tasks.update_exchange_rates()

    def test_credit(self):

        # Create a transaction
        session_id = "123"
        transaction = models.DownloadTransaction.objects.create()
        user_currency = settings.DEFAULT_PRICING_CURRENCY
        items = [self.test_song]
        transaction.prepare(items, description="Test download", session_id=session_id, ip="1.1.1.1", user_currency=user_currency)
        transaction.mark_payment_received()

        # Mock out outgoing Bitcoin payments
        with patch.object(blockchain, 'send_to_address') as mock_send:
            mock_send.return_value = "txhash_xyz"

            # Now credit the download
            credited = 0
            for store in models.Store.objects.all():
                credited += creditor.credit_store(store)
            self.assertEqual(1, credited)

        transaction = models.DownloadTransaction.objects.get(id=transaction.id)
        self.assertIsNotNone(transaction.credited_at)
        self.assertEquals("txhash_xyz", transaction.credit_transaction_hash)


class SignUpTestCase(TestCase):
    """ Check sign up form basic functionality. """

    def setUp(self):
        clear()
        models.update_initial_groups()

    def test_sign_up(self):
        data = dict(email="foo@example.com", password1="x", password2="x", store_url="https://example.com", artist_name="Foo Bar", currency=settings.DEFAULT_PRICING_CURRENCY)
        form = signup.SignupForm(data)
        assert form.is_valid(), form._errors
        form.create_user()

        store = models.Store.objects.all()[0]
        self.assertEqual("foo@example.com", store.operators.all()[0].username)


class WelcomeWizardTestCase(TestCase):
    """ Test welcome wizard functionality. """

    def setUp(self):
        clear()
        models.update_initial_groups()
        self.user = models.User.objects.create(username="foobar")

    def test_set_status(self):
        wizard = models.WelcomeWizard(self.user)
        wizard.set_step_status("check_store_details", True)

    def test_get_status(self):
        wizard = models.WelcomeWizard(self.user)
        self.assertFalse(wizard.get_step_statuses()["check_store_details"])
        wizard.set_step_status("check_store_details", True)
        self.assertTrue(wizard.get_step_statuses()["check_store_details"])


class CryptoassetsPaymentTestCase(TestCase):
    """See that we can receive payments using cryptoassets framework. """

    def setUp(self):
        models.DownloadTransaction.objects.all().delete()

        test_store = models.Store.objects.create(name="Test Store")
        test_store.currency = settings.DEFAULT_PRICING_CURRENCY
        test_store.store_url = "http://localhost:8000/store/test-store/"
        test_store.save()

        test_album = models.Album.objects.create(name="Test Album", store=test_store)
        test_album.fiat_price = Decimal("8.90")
        test_album.description = u"My very first album åäö"
        test_album.save()

        test_song1 = models.Song.objects.create(name="Song A", album=test_album, store=test_store)
        test_song1.fiat_price = Decimal("0.95")
        test_song1.save()

        self.test_store = test_store
        self.test_album = test_album
        self.test_song = test_song1

        redis = get_cache("default")
        redis.clear()
        tasks.update_exchange_rates()

    def test_create_receiving_address(self):
        session_id = "123"
        transaction = models.DownloadTransaction.objects.create()
        user_currency = "USD"
        items = [self.test_album, self.test_song]
        transaction.prepare(items, description="Test download", session_id=session_id, ip="1.1.1.1", user_currency=user_currency)

