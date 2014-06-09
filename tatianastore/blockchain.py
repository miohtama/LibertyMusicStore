"""

    blockchain wallet integration

"""

import logging
from decimal import Decimal

import requests

from django.utils.timezone import now
from django import http
from django.conf import settings

from . import models

URL = "https://blockchain.info/"

logger = logging.getLogger(__name__)


class BlockChainAPIError(Exception):
    pass


def create_new_receiving_address(label):
    """ Creates a new receiving address in BlockChain wallet.

    https://blockchain.info/merchant/$guid/new_address?password=$main_password&second_password=$second_password&label=$label
    """

    params = {
        "label": label,
        "password": settings.BLOCKCHAIN_WALLET_PASSWORD
    }

    url = URL + "merchant/%s/new_address" % settings.BLOCKCHAIN_WALLET_ID

    r = requests.get(url, params=params)
    data = r.json()
    logger.info("Generated blockchain.info wallet address %s", data["address"])
    return data["address"]


def send_to_wallet():
    """ Send money from blockchain wallet to somewhere else. """


def blockchain_received(request):
    """ Received Bitcoins to blockchain wallet address.

    Hook triggered by blockchain.info API.

    wget -S "http://localhost:8000/blockchain_received/?transaction_hash=x&value_in_btc=1&address=2"
    """

    transaction_hash = request.GET['transaction_hash']
    value = Decimal(request.GET['value']) / Decimal(100000000)
    address = request.GET['address']
    confirmations = int(request.GET.get('confirmations', -1))

    logger.info("Transaction received: %s BTC:%s address:%s confirmations:%d", transaction_hash, value, address, confirmations)

    try:
        t = models.DownloadTransaction.objects.get(btc_address=address)
    except models.DownloadTransaction.DoesNotExist:
        logger.error("Got blockchain_received() for unknown address %s", address)
        return http.HttpResponse("*fail")

    success = t.check_balance(value, transaction_hash)

    # Blockchain return values, don't know if meaningful
    return http.HttpResponse("*ok*") if success else http.HttpResponse("*error*")


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
