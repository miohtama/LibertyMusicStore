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


# Don't accidentally allow to run against the production Redis
assert settings.CACHES["default"]["LOCATION"] == "127.0.0.1:6379:10", "Don't run against production Redis"


class DownloadTransactionTestCase(TestCase):
    """ Test that we can create and retrieve download transactions.. """

    def setUp(self):
        models.DownloadTransaction.objects.all().delete()

        test_store = models.Store.objects.create(name="Test Store")
        test_store.currency = "USD"
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
        user_currency = "USD"
        items = [self.test_album, self.test_song]
        transaction.prepare(items, description="Test download", session_id=session_id, ip="1.1.1.1", user_currency=user_currency)

        transaction.mark_payment_received()

        content_manager = models.UserPaidContentManager(session_id)
        self.assertTrue(content_manager.has_item(self.test_song))
        self.assertTrue(content_manager.has_item(self.test_album))
