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
COIN_NAME = "Bitcoin"

COIN_NAME_SHORT = "BTC"

PAYMENT_SOURCE = "cryptoassets"

CRYPTOASSETS = {

    # You can use a separate database for cryptoassets,
    # or share the Django database. In any case, cryptoassets
    # will use a separate db connection.
    "database": {
        "url": "sqlite:////tmp/tatianastore.cryptoassets.sqlite",
        #"url": "postgresql://localhost/cryptoassets_test",
        "echo": False,
    },

    "coins": {
        # Locally running bitcoind in testnet
        "btc": {
            "backend": {
                "class": "cryptoassets.core.backend.bitcoind.Bitcoind",
                "url": "http://foo:bar@127.0.0.1:8332/",
                # Cryptoassets helper process will use this UNIX named pipe to communicate
                # with bitcoind
                "walletnotify": {
                    "class": "cryptoassets.core.backend.httpwalletnotify.HTTPWalletNotifyHandler",
                    "ip": "127.0.0.1",
                    "port": 28882
                },
            }
        },
    },

    # Bind cryptoassets.core event handler to Django dispacth wrapper
    "events": {
        "django": {
            "class": "cryptoassets.core.notify.python.InProcessNotifier",
            "callback": "cryptoassets.django.incoming.handle_tx_update"
        }
    }
}