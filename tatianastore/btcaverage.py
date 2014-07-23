"""

Minimal Bitcoin <-> currency exchange rate converter using bitcoinaverage.com API.

Do HTTP fetches using request library.

http://bitcoinaverage.com

http://docs.python-requests.org/en/latest/index.html

http://docs.python.org/2/library/shelve.html

https://pypi.python.org/pypi/redis/

Self testing::

    python btcrate.py

    # Macports
    sudo redis-server /opt/local/etc/redis.conf &
    python btcrate.py redis

"""

__author__ = "Mikko Ohtamaa http://opensourcehacker.com"
__license__ = "MIT"

import datetime
import calendar
from decimal import Decimal
import os
import shelve
import requests
import logging
import cPickle as pickle

# How often we attempt to refresh
REFRESH_DELAY = datetime.timedelta(hours=1)


API_URL = "https://api.bitcoinaverage.com/ticker/all"


logger = logging.getLogger(__name__)


class UnknownCurrencyException(Exception):
    """ The asked fiat currency was not available in bitcoinaverage.com data """


class Converter(object):
    """ Convert between BTC and fiat currencies.

    Use bitcoinaverage.com data, casche the result persistently on the disk using Python shelve module.

    """

    def __init__(self, refresh_delay=REFRESH_DELAY, api_url=API_URL):
        """ Construct a converter.

        :param refresh_delay: datetime.timedelta object how often we ask new data from API
        """
        self.refresh_delay = refresh_delay
        self.api_url = api_url

    def convert(self, source, target, amount, update, determiner="24h_avg"):
        """ Convert value between source and target currencies.

        :param source: three letter currency code of the source currency

        :param target: three letter currency code of the target currency

        :param update: Set to False to always force to use externally updated data.
                       This is to prevent thundering herd problem.

        :param amount: The amount to convert in BTC.
        """

        assert isinstance(amount, Decimal), "Only decimal.Decimal() inputs allowed, got %s" % amount

        # Refresh from cache if needed
        if update and not self.is_up_to_date():
            self.update()

        source = source.upper()
        target = target.upper()

        if source == target:
            # No conversion needed
            return amount

        assert "BTC" in (source, target), "We can only convert to BTC forth and back"

        # Swap around if we are doing backwards conversion
        original_target = target
        if source == "BTC":
            inverse = True
            source, target = target, source
        else:
            inverse = False

        data = self.get_data()
        if data is None:
            raise UnknownCurrencyException("Currency data not available - check currency data cache storage")

        currency_data = data.get(source)
        if not currency_data:
            raise UnknownCurrencyException("The currency %s was not available in data %s" % (source, self.api_url))

        rate = currency_data[determiner]
        if not rate:
            logger.error("currency_data %s", currency_data)
            raise UnknownCurrencyException("The currency %s lacks rate variable %s" % (source, determiner))

        assert rate > 0, "Rate was %s", rate

        if inverse:
            result = amount * Decimal(rate)
        else:
            result = amount / Decimal(rate)

        if original_target == "BTC":
            # Present BTC with 8 decimals
            result = result.quantize(Decimal("1.00000000"))
        else:
            result = result.quantize(Decimal("1.00"))

        return result

    def update(self):
        """ Attempt to update the market data from external server.

        Gracefully fail in the case of connectivity issues, etc.

        :return: True if the update succeeded
        """

        try:
            r = requests.get(self.api_url)
            self.set_data(r.json())
            return True
        except Exception as e:
            logger.error("Could not refresh market data: %s %s", self.api_url, e)
            logger.exception(e)
            return False

    def get_data(self):
        """ Return currently stored data in Python nested dictionary format. """
        raise NotImplementedError("Subclass must implement")

    def set_data(self, data):
        """ Set the current market data in cache.

        :param data: External data as Python data structures

        """
        raise NotImplementedError("Subclass must implement")

    def is_up_to_date(self):
        """ Check whether we should refresh our data.
        """
        raise NotImplementedError("Subclass must implement")


class ShelveConverter(Converter):
    """ Store data in Python shelve backend.

    Good for single process applications / light-weight multiprocess applications.
    """

    def __init__(self, fpath, refresh_delay=REFRESH_DELAY, api_url=API_URL):
        """ Construct a converter.

        :param fpath: Path to a file where we cache the results.
                      The cache is persistent; in the case we do a cold start
                      and API is not available we use cached exchange data.

        """
        super(ShelveConverter, self).__init__(refresh_delay, api_url)
        self.last_updated = None

        self.data = shelve.open(fpath)

        if os.path.exists(fpath):
            self.last_updated = datetime.datetime.fromtimestamp(os.path.getmtime(fpath))

    def set_data(self, data):
        self.data["bitcoinaverage"] = data
        self.data["bitcoin_updated"] = datetime.datetime.utcnow()
        self.data.sync()

    def get_data(self):
        return self.data["bitcoinaverage"]

    def is_up_to_date(self):
        if not self.data["bitcoin_updated"]:
            return False

        return datetime.datetime.utcnow() < self.data["bitcoin_updated"] + self.refresh_delay

    def convert(self, source, target, amount, update=True, determiner="24h_avg"):
        """ Shelve is run with a single process, always try to update itself because there is no external update task.

        :return: decimal.Decimal

        """
        return super(ShelveConverter, self).convert(source, target, amount, update, determiner)


class RedisConverter(Converter):
    """ Multi-process aware converter which stores external data persistently in Redis backend.

    .. note ::

        Never call convert(update=True) directly from a web worker process.
        Only external (Celery) task process is allowed to update to avoid
        thundering herd problem.

    """

    def __init__(self, redis, refresh_delay=REFRESH_DELAY, api_url=API_URL):
        """ Construct a converter.

        :param redis: redis.Redis instance. Must be constructed somewhere else.

        :param fpath: Path to a file where we cache the results.
                      The cache is persistent; in the case we do a cold start
                      and API is not available we use cached exchange data.

        """
        super(RedisConverter, self).__init__(refresh_delay, api_url)
        self.redis = redis

    def convert(self, source, target, amount, update=False, determiner="24h_avg"):
        """ Do not allow web processes to try to update the date.

        :return: decimal.Decimal
        """
        return super(RedisConverter, self).convert(source, target, amount, update, determiner)

    def set_data(self, data):
        # Don't set expiration as we want to hold the data indefinitely
        # http://stackoverflow.com/questions/15219858/how-to-store-a-complex-object-in-redis-using-redis-py
        self.redis.set("bitcoinaverage", pickle.dumps(data))
        self.redis.set("bitcoinaverage_updated", calendar.timegm(datetime.datetime.utcnow().utctimetuple()))

    def get_data(self):
        val = self.redis.get("bitcoinaverage")
        return pickle.loads(val) if val else None

    def is_up_to_date(self):

        timestamp = self.redis.get("bitcoinaverage_updated")
        if not timestamp:
            return False

        last_updated = datetime.datetime.fromtimestamp(float(timestamp))

        return datetime.datetime.utcnow() < last_updated + self.refresh_delay

    def tick(self):
        """ Run a periodical worker task to see if we need to update.
        """
        if not self.is_up_to_date():
            self.update()

# Simple self-test
if __name__ == "__main__":

    import tempfile
    import sys

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.ERROR)

    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

    # Get random rate from bitcoinaverage.com

    if len(sys.argv) == 2 and sys.argv[1] == "redis":
        # Redis testing
        import redis
        redis = redis.StrictRedis(host='localhost', port=6379, db=0)
        converter = RedisConverter(redis)
    else:
        # Shelve testing
        fname = tempfile.mktemp()
        converter = ShelveConverter(fname)

    assert converter.update()

    assert "24h_avg" in converter.get_data()["USD"]

    # Test failure mode, that we get data from persistent cache
    # because our API server is down (we point to dummy server)
    if isinstance(converter, ShelveConverter):
        converter = ShelveConverter(fname, api_url="http://localhost")
    else:
        converter = RedisConverter(redis, api_url="http://localhost")

    # Do a failed update
    root_logger.setLevel(logging.FATAL)
    assert not converter.update()
    root_logger.setLevel(logging.ERROR)

    assert "24h_avg" in converter.get_data()["USD"]

    p1 = converter.convert("btc", "usd", Decimal("1.0"))
    p2 = converter.convert("usd", "btc", Decimal("1.0"))

    assert p1*p2 == Decimal("1.0")
