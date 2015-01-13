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

from cryptoassets.core.coin import registry as coin_registry

from cryptoassets.django import assetdb
from cryptoassets.django.signals import txupdate
from cryptoassets.django.app import get_cryptoassets

logger = logging.getLogger(__name__)


def get_wallet(session):
    """Return the master shared wallet used to receive payments. """
    cryptoassets = get_cryptoassets()
    wallet_class = cryptoassets.coins.get(settings.PAYMENT_CURRENCY).wallet_model
    wallet = wallet_class.get_or_create_by_name("default", session)
    return wallet


def create_new_receiving_address(store_id, label):
    """ Creates a new receiving address in cryptoassets wallet.

    https://blockchain.info/merchant/$guid/new_address?password=$main_password&second_password=$second_password&label=$label
    """

    @assetdb.managed_transaction
    def tx(session):
        wallet = get_wallet(session=session)
        account = wallet.get_or_create_account_by_name("Store {}".format(store_id))
        session.flush()  # account gets id
        _addr = wallet.create_receiving_address(account, label)
        logging.info("Created receiving address %s for store %d", _addr.address, store_id)
        address = _addr.address
        return address

    return tx()


def get_store_account_info(store):
    """Return (account id, balance) tuple
    """
    @assetdb.managed_transaction
    def tx(session):
        wallet = get_wallet(session=session)
        account = wallet.get_or_create_account_by_name("Store {}".format(store.id))
        id, balance = account.id, account.balance
        session.commit()
        return id, balance

    return tx()


def archive(addresses):
    """ Archive the used address. """

    # ATM doesn't do anything
    return


def send_to_address(store, address, btc_amount, note):
    """ Send money from blockchain wallet to somewhere else. """

    account_id, balance = get_store_account_info(store)
    logger.info("Sending from account %s, has %s BTC, sending %s to %s", account_id, balance, btc_amount, address)

    @assetdb.managed_transaction
    def tx(session):
        wallet = get_wallet(session=session)
        account = wallet.get_or_create_account_by_name("Store {}".format(store.id))

        # This is completely unnecessary check,
        # but is now here for debugging BlockChain API problems
        assert account.balance >= btc_amount, "Not enough funds in the wallet on account %s, got %s need %s" % (account.id, account.balance, btc_amount)

        tx = wallet.send(account, address, btc_amount, note)

        logger.debug("Balance left after send: %s", account)

        return tx.id

    return tx()


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
    value = data['amount']
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
        logger.info("Already completed")
        return

    success = t.check_balance(value, transaction_hash)
    if not success:
        logger.error("The transaction %s had not enough value", transaction_hash)

    logger.info("DownloadTransaction processed %d", t.id)


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
