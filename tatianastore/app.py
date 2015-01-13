import os
import sys
import logging

from django.apps import AppConfig
from django.conf import settings

from cryptoassets.django.app import get_cryptoassets


logger = logging.getLogger(__name__)


class TatianastoreConfig(AppConfig):
    name = 'tatianastore'
    verbose_name = "Liberty Music Store core"

    def ready(self):

        # Register signal handlers
        from tatianastore import payment
        from tatianastore import signals

        # Set 1 confirmations required for finalized payments
        if settings.PAYMENT_CURRENCY == "btc":
            btc = get_cryptoassets().coins.get("btc")
            btc.coin_description.Transaction.confirmation_count = 1