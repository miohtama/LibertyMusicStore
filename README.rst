
.. contents:: :local:

Introduction
---------------

`Liberty Music Store is a prototype MP3 store taking Bitcoin payments. <https://libertymusicstore.net>`_

The project is 100% open source. You can use this as an example project for your Django and Bitcoin services.

Stack
------

* `Python 3.4 <https://python.org>`_ - core programming language

* `Django <https://www.djangoproject.com/>`_ - Python web framework

* `Bootstrap <http://getbootstrap.com/>`_ - Layout

* `uWSGI <http://uwsgi-docs.readthedocs.org/en/latest/>`_ - web server

* `Nginx <http://nginx.org/>`_ - web server

* PostgreSQL / SQLite - database

* Redis - database (sessions, task queue)

* `Supervisor <http://supervisord.org/>`_ - process launch and management

* `cryptoassets.core <http://cryptoassetscore.readthedocs.org/en/latest/>`_ / `cryptoassets.django <https://bitbucket.org/miohtama/cryptoassets.django>`_ - Bitcoin payment handling

* `huey <http://huey.readthedocs.org/>`_  - asynchronous and background tasks

* `bitcoinaddress.js <http://github.com/miohtama/bitcoinaddress.js>`_ - Bitcoin address interaction in web browser

* `bitcoinprices.js <https://github.com/miohtama/bitcoin-prices>`_ - real-time currency conversion

* `Sentry <http://sentry.readthedocs.org/>`_ - logging

* `Duplicity <http://duplicity.nongnu.org/>`_ - backups

* `ffmpeg <https://www.ffmpeg.org/>`_ - audio processing

Development environment setup
------------------------------

PostgreSQL is recommened. SQLite 3 won't work because it locks the full database on a write, causing conflict with page requests, AJAX requests and cryptoassets helper service accessing the database at the same moment.

Checkout::

    git checkout
    git submodule update --init --recursive

Setup virtualenv::

    export PATH=/usr/local/mysql/bin:$PATH
    virtualenv-2.7 venv
    source venv/bin/activate
    # https://bitbucket.org/nicfit/eyed3/issue/80/pypi-hosted-release
    pip install --allow-all-external -r requirements.txt

Example ``local_settings.py`` for development::

    import os
    import sys

    ALLOWED_HOSTS = ["localhost:8000", "localhost:8090", "libertymusicstore.net:9999"]

    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

    RECAPTCHA_PUBLIC_KEY = 'x'
    RECAPTCHA_PRIVATE_KEY = 'y'
    RECAPTCHA_USE_SSL = True

    PUBLIC_URL = "http://localhost:8000"


    # FB test settings
    if "runsslserver" in sys.argv:
        os.environ["HTTPS"] = "on"
        SITE_URL = "https://libertymusicstore.net:9999"
    else:
        SITE_URL = "http://localhost:8000"

    HUEY = {
        'backend': 'huey.backends.redis_backend',  # required.
        'name': 'Huey Redis',
        'connection': {'host': 'localhost', 'port': 6379},
        'always_eager': True, # Defaults to False when running via manage.py run_huey
        'consumer_options': {'workers': 3},
    }

    # Facebook development
    FACEBOOK_SECRET_KEY = "x"

    #from cryptoassets.core.coin.bitcoin.models import BitcoinWallet
    #PAYMENT_WALLET_CLASS = BitcoinWallet

    # TESTNET settings
    CRYPTOASSETS = {

        # You can use a separate database for cryptoassets,
        # or share the Django database. In any case, cryptoassets
        # will use a separate db connection.
        "database": {
            "url": "postgresql://localhost/cryptoassets_copy",
            "echo": False,
        },

        "coins": {
            # Locally running bitcoind in testnet
            "btc": {
                "backend": {
                    "class": "cryptoassets.core.backend.blockio.BlockIo",
                    "api_key": "x",
                    "network": "btctest",
                    "pin": "x",
                    # Cryptoassets helper process will use this UNIX named pipe to communicate
                    # with bitcoind
                    "walletnotify": {
                        "class": "cryptoassets.core.backend.sochainwalletnotify.SochainWalletNotifyHandler",
                        "pusher_app_key": "x"
                    },
                }
            },
        },

        # Bind cryptoassets.core event handler to Django dispacth wrapper
        "events": {
            "django": {
                "class": "cryptoassets.core.event.python.InProcessEventHandler",
                "callback": "cryptoassets.django.incoming.handle_tx_update"
            }
        },

        "status_server": {
            "ip": "127.0.0.1",
            "port": 9001
        }
    }


Setup empty database::

    python manage.py syncdb
    python manage.py migrate tatianstore

    # This creates some initial users and stuff
    # This scripts reads stuff from sample CD folder (copyrighted),
    # so ask for a copy
    echo "exec(open('./bin/populate.py').read())" | python manage.py shell

Fix ``readline`` package on OSX::

    easy_install -U readline

Start the server::

    python manage.py runserver

Production setup on Ubuntu
----------------------------

Install::

    apt-get install postgresql libncurses5-dev redis-server python-virtualenv openssl
    apt-get install build-essential git-core libfreetype6-dev libmemcached-dev libxml2-dev libxslt1-dev libjpeg-dev libpng12-dev gettext git

Create databases::

    sudo -i -u postgresq
    createdb cryptoassets_production
    createdb tatianastore_production

Create venv::

    python3.4 -m venv --copies venv

... TODO

FFMPEG
--------

FFMPEG is required in order to create the prelisten samples.

Installing on OSX::

    brew install ffmpeg --with-vpx --with-vorbis --with-libvorbis --with-vpx --with-vorbis --with-theora --with-libogg --with-libvorbis --with-gpl --with-version3 --with-nonfree --with-postproc --with-libaacplus --with-libass --with-libcelt --with-libfaac --with-libfdk-aac --with-libfreetype --with-libmp3lame --with-libopencore-amrnb --with-libopencore-amrwb --with-libopenjpeg --with-openssl --with-libopus --with-libschroedinger --with-libspeex --with-libtheora --with-libvo-aacenc --with-libvorbis --with-libvpx --with-libx264 --with-libxvid

Running tests
----------------

Ex::

    python manage.py test tatianastore --settings=tatianastore.test_settings

Production setup
-----------------

Dependencies::

    apt-get install supervisor postgresql postgresql-server-dev-all
    source /srv/django/tatianastore/venv/bin/activate
    pip install psycopg2

ffmpeg::

    cd /tmp
    wget http://johnvansickle.com/ffmpeg/releases/ffmpeg-2.2.1-64bit-static.tar.bz2
    tar -xf ffmpeg-2.2.1-64bit-static.tar.bz2
    mv ffmpeg-2.2.1-64bit-static/ffmpeg /usr/local/bin

Deployment::

    ssh tatianastore
    git pull && supervisorctl restart tatianastore_uwsgi

Taking SQL dump::

    sudo -u postgres pg_dump tatianastore > backup.sql

Restoring SQL dump::

    sudo -u postgres psql -d tatianastore_production -f backup.sql

Creatin htpasswd file for the status server::

    apt-get install apache2-utils
    htpasswd -c status.htpasswd  status

More

* https://www.digitalocean.com/community/tutorials/how-to-install-and-configure-django-with-postgres-nginx-and-gunicorn

* http://od-eon.com/blogs/calvin/postgresql-cheat-sheet-beginners/

Facebook app testing
----------------------

TODO: deprecated

Register a faux app on Facebook.

Use `runsslserver` to run a local development server.

Tunnel localhost:8000 to remoto IP:9999.

Set this publicly accessible port to your FB app settings.

Making a dummy BTC payment when running in FB test mode::

    wget -S --no-check-certificate --output-document="-" "https://libertymusicstore.net:9999/blockchain_received/?transaction_hash=x&value=10000&address=1CAEmjdasqskBEJMsCeY9wUeBuofiw21cA"

Other
-----

Codename ``tatianastore`` is used through the project.

``test-song.mp3`` is *I dunno* by *Grapes*.

* http://ccmixter.org/files/grapes/16626

Author
------

Mikko Ohtamaa (`blog <https://opensourcehacker.com>`_, `Facebook <https://www.facebook.com/?q=#/pages/Open-Source-Hacker/181710458567630>`_, `Twitter <https://twitter.com/moo9000>`_, `Google+ <https://plus.google.com/u/0/103323677227728078543/>`_)



