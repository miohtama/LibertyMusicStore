.. contents:: :local:

Introduction
---------------

`**Libery Music Store** is a prototype MP3 store taking Bitcoin payments. <https://libertymusicstore.net>`_

Dependencies

* SQL database (SQLite for development, PostgreSQL for production recommended)

* Redis

* Django

* Supervisor (production deployment only)

blockchain.info API is used for the receiving transactions and Bitcoin wallet management.

Development environment setup
------------------------------

Setup virtualenv::

    export PATH=/usr/local/mysql/bin:$PATH
    virtualenv-2.7 venv
    source venv/bin/activate
    pip install -r requirements.txt

Example ``local_settings.py``::

    BLOCKCHAIN_WALLET_ID = "xxx-yyy"
    BLOCKCHAIN_WALLET_PASSWORD = "password"

    ALLOWED_HOSTS = ["localhost:8000", "localhost:8090"]

    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

    PUBLIC_URL = "http://localhost:8000"

Setup empty database::

    python manage.py syncdb --noinput && python manage.py migrate
    echo "execfile('./tatianastore/populate.py')" | python manage.py shell

Fix ``readline`` package on OSX::

    easy_install -U readline

Production setup on Ubuntu
----------------------------

Install::

    apt-get install libncurses5-dev redis-server python-virtualenv openssl
    apt-get install build-essential git-core libfreetype6-dev libmemcached-dev libxml2-dev libxslt1-dev libjpeg-dev libpng12-dev gettext python-virtualenv virtualenvwrapper git libmysqlclient-dev python-dev
    virtualenv venv
    pip install distribute
    pip install -r requirements.txt

Ex::

    GRANT ALL ON tatianastore.* TO 'tatianastore'@'localhost' identified by 'tatianastore';

    python manage.py reset tatianastore
    python manage.py syncdb
    python manage.py migrate tatianastore zero

Reset::

    python manage.py reset_db --router=default --noinput && python manage.py syncdb --noinput && python manage.py migrate
    echo "execfile('./tatianastore/sample.py')" | python manage.py shell

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

More

* https://www.digitalocean.com/community/tutorials/how-to-install-and-configure-django-with-postgres-nginx-and-gunicorn

* http://od-eon.com/blogs/calvin/postgresql-cheat-sheet-beginners/

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
    </style>

Some fonts
++++++++++++

Examples::

    <link href='https://fonts.googleapis.com/css?family=Libre+Baskerville&amp;subset=latin,latin-ext' rel='stylesheet' type='text/css'>

Author
------

Mikko Ohtamaa (`blog <https://opensourcehacker.com>`_, `Facebook <https://www.facebook.com/?q=#/pages/Open-Source-Hacker/181710458567630>`_, `Twitter <https://twitter.com/moo9000>`_, `Google+ <https://plus.google.com/u/0/103323677227728078543/>`_)

Contact for work and consulting offers.


