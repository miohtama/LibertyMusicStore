"""

    Download payments crediting business logic.

"""

import logging
from decimal import Decimal

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.db.models import Sum
from django.utils.timezone import now
from django.db import transaction

from . import blockchain
from . import emailer

import bitcoinaddress
from retools.lock import Lock


logger = logging.getLogger(__name__)


def credit_transactions(store, transactions):
    """ Make the Bitcoin transaction crediting the store owner. """

    sums = transactions.aggregate(Sum('btc_amount'))
    total = sums.get("btc_amount__sum") or Decimal("0")

    logger.info(u"Crediting store %d %s total amount %s", store.id, store.name, total)
    tx_hash = blockchain.send_to_address(store.btc_address, total, "Crediting for %s" % store.name)
    transactions.update(credit_transaction_hash=tx_hash, credited_at=now())


def credit_store(store):
    """
    :return: Number of download transactions credited
    """

    credited = 0

    if not store.email:
        logger.error("Store lacks email %s", store.name)
        return 0

    if not store.btc_address:
        logger.error("Store lacks BTC address %s", store.name)
        return 0

    if not bitcoinaddress.validate(store.btc_address):
        logger.error("Store %s not valid BTC address %s", store.name, store.btc_address)
        return 0

    # Some additional protection against not accidentelly running
    # parallel with distributed lock
    with Lock("credit_store_%d" % store.id):

        # Split up to two separate db transactions
        # to minitize the risk of getting blockchain
        # and db out of sync because of mail errors and such

        # Which of the transactions we have not yet credited
        uncredited_transaction_ids = []

        with transaction.atomic():
            uncredited_transactions = store.downloadtransaction_set.filter(credited_at__isnull=True, btc_received_at__isnull=False)

            uncredited_transaction_ids = list(uncredited_transactions.values_list("id", flat=True))

            sums = uncredited_transactions.aggregate(Sum('btc_amount'))
            total = sums.get("btc_amount__sum") or Decimal("0")

            if total == 0:
                logger.info("Store %s no transactions to credit", store.name)
                return 0

            credit_transactions(store, uncredited_transactions)

        # Reload after tx commit
        uncredited_transactions = store.downloadtransaction_set.filter(id__in=uncredited_transaction_ids)

        # Archive addresses as used
        blockchain.archive(uncredited_transactions.values_list("btc_address", flat=True))

        mail_store_owner(store, "Liberty Music Store payments", "email/credit_transactions.html", dict(store=store, transactions=uncredited_transactions))

        credited += uncredited_transactions.count()

        logger.debug("Credited %d transcations", credited)

    return credited