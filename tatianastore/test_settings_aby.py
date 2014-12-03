# AppleByte altcoin test settings

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

PAYMENT_CURRENCY = "aby"

CRYPTOASSETS = {

    # You can use a separate database for cryptoassets,
    # or share the Django database. In any case, cryptoassets
    # will use a separate db connection.
    "database": {
        # "url": "sqlite:////tmp/payments.sqlite",
        "url": "postgresql://localhost/applebyteassets",
        "echo": False,
    },

    # Locally running bitcoind in testnet
    "coins": {
        "aby": {
            "backend": {
                "class": "cryptoassets.core.backend.bitcoind.Bitcoind",
                "url": "http://applebyterpc:7gqYmSECoaqwDbB7esnNqv1xsDfZhwQuddP8djBZEHPC@127.0.0.1:8607/",
                # Cryptoassets helper process will use this UNIX named pipe to communicate
                # with bitcoind
                "walletnotify": {
                    "class": "cryptoassets.core.backend.httpwalletnotify.HTTPWalletNotifyHandler",
                    "ip": "127.0.0.1",
                    "port": 28882
                },
            },
        },
    },

    # List of cryptoassets notification handlers.
    # Use this special handler to convert cryptoassets notifications to Django signals.
    "notify": {
        "django": {
            "class": "cryptoassets.core.notify.python.InProcessNotifier",
            "callback": "cryptoassets.django.incoming.handle_tx_update"
        }
    }
}