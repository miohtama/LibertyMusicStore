"""

    Payment processing

"""

import logging
import transaction
from decimal import Decimal

import requests

from django.utils.timezone import now
from django import http
from django.conf import settings
from django.dispatch import receiver

from . import models

from cryptoassets.core import configure
from cryptoassets.core.models import DBSession
from cryptoassets.core.models import DBSession
from cryptoassets.core.coin import registry as coin_registry

from sqlalchemy.orm.session import Session
from cryptoassets.django import dbsession
from cryptoassets.django.signals import txupdate

URL = "https://blockchain.info/"

logger = logging.getLogger(__name__)


def get_wallet(session):
    """Return the master shared wallet used to receive payments. """
    wallet_class = coin_registry.get_wallet_model(settings.PAYMENT_CURRENCY)
    wallet = wallet_class.get_or_create_by_name("default", session)
    return wallet


def create_new_receiving_address(store_id, label):
    """ Creates a new receiving address in cryptoassets wallet.

    https://blockchain.info/merchant/$guid/new_address?password=$main_password&second_password=$second_password&label=$label
    """

    session = dbsession.open_session()
    wallet = get_wallet(session=session)
    account = wallet.get_or_create_account_by_name("Store {}".format(store_id))
    _addr = wallet.create_receiving_address(account, label)
    logging.info("Created receiving address %s for store %d", _addr.address, store_id)
    address = _addr.address
    session.commit()

    return address


def balance():
    """ Return BlockChain wallet balance in BTC.
    """
    session = open_non_closing_session()
    wallet = get_wallet(session=session)
    session.commit()
    return wallet.balance


def archive(addresses):
    """ Archive the used address. """

    for address in addresses:
        params = {
            "password": settings.BLOCKCHAIN_WALLET_PASSWORD,
            "address": address,
        }

        logger.info("Archiving address %s", address)
        url = URL + "merchant/%s/archive_address" % settings.BLOCKCHAIN_WALLET_ID
        r = requests.get(url, params=params)
        data = r.json()

        assert "archived" in data, "Got blockchain reply %s" % data


def send_to_address(address, btc_amount, note):
    """ Send money from blockchain wallet to somewhere else. """

    # This is completely unnecessary check,
    # but is now here for debugging BlockChain API problems
    balance_ = balance()
    assert Decimal(balance_) >= Decimal(btc_amount), "Not enough funds in BlockChain wallet, got %s need %s" % (balance_, btc_amount)

    logger.info("Sending from BlockChain wallet %s, has %s BTC, sending %s to %s", settings.BLOCKCHAIN_WALLET_ID, balance_, btc_amount, address)

    satoshi_amount = int(btc_amount * Decimal(100000000))

    params = {
        "password": settings.BLOCKCHAIN_WALLET_PASSWORD,
        "amount": satoshi_amount,
        "note": note,
        "to": address,
    }

    url = URL + "/merchant/%s/payment" % settings.BLOCKCHAIN_WALLET_ID

    r = requests.get(url, params=params)
    data = r.json()

    tx_hash = data.get("tx_hash")
    assert tx_hash, "BlockChain did not return a transaction hash %s" % data

    return tx_hash

@receiver(txupdate)
def txupdate_received(event_name, data, **kwargs):
    """ Received transaction update from cryptoassets.core.

    This handler is run cryptoassets helper service process.

    Start the transaction service::

        python manage.py cryptoassetshelper

    Start the server::

        python manage.py runserver

    Go to http://localhost:8000/store/test-store/embed-preview/

    Start buying a song

    Send in payment from block.io testnet

    Wait 10 seconds.
    """

    transaction_hash = data["txid"]
    value = Decimal(data['amount']) / Decimal(100000000)
    address = data['address']
    confirmations = int(data.get('confirmations', -1))

    logger.info("Transaction received: %s BTC:%s address:%s confirmations:%d", transaction_hash, value, address, confirmations)

    try:
        t = models.DownloadTransaction.objects.get(btc_address=address)
    except models.DownloadTransaction.DoesNotExist:
        logger.warn("Got txupdate for unknown DownloadTransaction, address %s", address)
        return

    if t.btc_received_at:
        # Already complete
        return

    success = t.check_balance(value, transaction_hash)
    if not success:
        logger.error("The transaction %s had not enough value", transaction_hash)


def get_all_address_data():
    """ Return the balances of all addresses in the format:

    https://blockchain.info/api/blockchain_wallet_api
    """

    params = {
        "password": settings.BLOCKCHAIN_WALLET_PASSWORD
    }

    url = URL + "merchant/%s/list" % settings.BLOCKCHAIN_WALLET_ID

    r = requests.get(url, params=params)
    data = r.json()

    if "error" in data:
        logger.error("Bad reply from blockchain.info %s", data)
        raise BlockChainAPIError(data["error"])
    if "addresses" not in data:
        logger.error("Bad reply from blockchain.info %s", data)
        raise BlockChainAPIError("Did not get proper reply")
    else:
        for address in data["addresses"]:
            yield address


def force_check_old_address(tx):
    """ Check if the transaction has come through.

    :return True if the transaction has succeeded
    """

    # TODO
    return None

    if tx.btc_received_at:
        # Already paid
        return True

    address_class = coin_registry.get_address_model(settings.PAYMENT_CURRENCY)
    address = None

    # Find address status on blockchain.info
    # TODO: optimize
    addresses = get_all_address_data()
    for address in addresses:
        if address["address"] == tx.btc_address:
            break
    else:
        return False

    try:

        if tx.get_status() != "pending":
            # Cancelled, confirmed, etc.
            return False

        value = address["total_received"] / Decimal(100000000)

        if tx.check_balance(value, transaction_hash=""):
            return True

    except BlockChainAPIError as e:
        logger.error("BlockChain wallet service error: %s" % e.message)

    return False
