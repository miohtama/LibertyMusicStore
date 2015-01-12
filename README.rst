.. contents:: :local:

Introduction
---------------

`Liberty Music Store is a prototype MP3 store taking Bitcoin payments. <https://libertymusicstore.net>`_

Dependencies
--------------

In order to get this running you need to install:

* SQL database (SQLite for development, PostgreSQL for production recommended)

* Redis

* Django

* Supervisor (production deployment only)

blockchain.info API is used for the receiving transactions and Bitcoin wallet management.

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

Example ``local_settings.py``::

    BLOCKCHAIN_WALLET_ID = "xxx-yyy"
    BLOCKCHAIN_WALLET_PASSWORD = "password"

    ALLOWED_HOSTS = ["localhost:8000", "localhost:8090"]

    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

    PUBLIC_URL = "http://localhost:8000"

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

You should now able to access generated test store

* http://localhost:8000/store/test-store/embed-preview/

Production setup on Ubuntu
----------------------------

Install::

    apt-get install postgresql libncurses5-dev redis-server python-virtualenv openssl
    apt-get install build-essential git-core libfreetype6-dev libmemcached-dev libxml2-dev libxslt1-dev libjpeg-dev libpng12-dev gettext git

Ex::

    GRANT ALL ON tatianastore.* TO 'tatianastore'@'localhost' identified by 'tatianastore';

    python manage.py reset tatianastore
    python manage.py syncdb
    python manage.py migrate tatianastore zero

Reset::

    python manage.py reset_db --router=default --noinput && python manage.py syncdb --noinput && python manage.py migrate
    echo "execfile('./tatianastore/sample.py')" | python manage.py shell

Nginx:

    TODO

FFMPEG
--------

FFMPEG is required in order to create the prelisten samples.

Installing on OSX::

    brew install ffmpeg --with-vpx --with-vorbis --with-libvorbis --with-vpx --with-vorbis --with-theora --with-libogg --with-libvorbis --with-gpl --with-version3 --with-nonfree --with-postproc --with-libaacplus --with-libass --with-libcelt --with-libfaac --with-libfdk-aac --with-libfreetype --with-libmp3lame --with-libopencore-amrnb --with-libopencore-amrwb --with-libopenjpeg --with-openssl --with-libopus --with-libschroedinger --with-libspeex --with-libtheora --with-libvo-aacenc --with-libvorbis --with-libvpx --with-libx264 --with-libxvid

Running tests
----------------

Ex::

    python manage.py test tatianastore --settings=tatianastore.test_settings

Running manual tests against the blockchain wallet
----------------------------------------------------

Build a tunnel to a publicly accessible server::

    bin/tunnel-blockchain-callback.sh

Make sure you have your tunneled IP and port in blockchain account notifications::

    http://1.2.3.4:4000/blockchain_received/

Do a test payment.

UWSGI
-------

Ex::

    uwsgi uwsgi_test.ini

Stop::

    pkill -f uwsgi

Restart::

    pkill -f uwsgi ; sleep 1; uwsgi uwsgi.prod.ini

Populate cache::

    from decimal import Decimal
    from tatianastore.models import get_rate_converter
    converter = get_rate_converter()
    converter.update()
    print converter.convert("btc", "usd", Decimal("1.0"))

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


More

* https://www.digitalocean.com/community/tutorials/how-to-install-and-configure-django-with-postgres-nginx-and-gunicorn

* http://od-eon.com/blogs/calvin/postgresql-cheat-sheet-beginners/

Facebook app testing
----------------------

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

Dark theme example
+++++++++++++++++++++

Extra HTML for the store to make it white on black::

    <link href='http://fonts.googleapis.com/css?family=Volkhov' rel='stylesheet' type='text/css'>
    <style>
        body {
           background: black;
           color: #aaa;
           margin: 20px;
        }

        h1, h3 {
           font-family: "Volkhov",serif;
        }

        .btn-default {
            background: #666;
            color: white;
        }

        /* QR code must be on the white background or BlockChain mobile wallet does not pick it up */
        .bitcoin-address-qr-container {
            padding: 40px 0;
            background: white;
        }
    </style>

Some fonts
++++++++++++

Examples::

    <link href='https://fonts.googleapis.com/css?family=Libre+Baskerville&amp;subset=latin,latin-ext' rel='stylesheet' type='text/css'>

Author
------

Mikko Ohtamaa (`blog <https://opensourcehacker.com>`_, `Facebook <https://www.facebook.com/?q=#/pages/Open-Source-Hacker/181710458567630>`_, `Twitter <https://twitter.com/moo9000>`_, `Google+ <https://plus.google.com/u/0/103323677227728078543/>`_)

Contact for work and consulting offers.


