from .settings import *

# make tests faster
SOUTH_TESTS_MIGRATE = False

DATABASES['default'] = {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': ':memory:',
}

LOGGING["loggers"]["django.db.backends"] = {
    "level": "WARN",
    'handlers': ['rainbow'],
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Use Redis database 10, so that we don't conflict with real data
CACHES = {
    "default": {
        "BACKEND": "redis_cache.cache.RedisCache",
        "LOCATION": "127.0.0.1:6379:10",
        "OPTIONS": {
            "CLIENT_CLASS": "redis_cache.client.DefaultClient",
            'CONNECTION_POOL_KWARGS': {'max_connections': 10},
        }
    }
}

# Don't mix test uploads with actual content
MEDIA_ROOT = "media/test"

HUEY = {
    'backend': 'huey.backends.redis_backend',  # required.
    'name': 'Huey Redis',
    'connection': {'host': 'localhost', 'port': 6379},
    'always_eager': True, # Execute background tasks immediately
    'consumer_options': {'workers': 3},
}


#: Human readable labels
COIN_NAME = "AppleByte"

COIN_NAME_SHORT = "ABY"

PAYMENT_SOURCE = "cryptoassets"

#from cryptoassets.core.coin.bitcoin.models import BitcoinWallet
#PAYMENT_WALLET_CLASS = BitcoinWallet

PAYMENT_CURRENCY = "btc"

PAYMENT_CONFIG = {
    "database": {
        "url": "sqlite:////tmp/payments.sqlite"
    },

    # What cryptocurrencies we are configuring to the database
    "models": {
        "btc": "cryptoassets.core.coin.bitcoin.models"
    },

    # Locally running bitcoind in testnet
    "backends": {
        "btc": {
            "class": "cryptoassets.core.backend.bitcoind.Bitcoind",
            "url": "http://foo:bar@127.0.0.1:8332/"
        }
    }
}