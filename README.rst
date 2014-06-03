**Libery Music Store** is a prototype MP3 store taking Bitcoin payments.

Dependencies

* SQL database (any, defaults to SQLite)

* Redis

* Django

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


Running tests
----------------

Ex::

    python manage.py test --settings=tatianastore.test_settings tatianastore

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

Other
-----

Codename ``tatianastore`` is used through the project.

``test-song.mp3`` is *I dunno* by *Grapes*.

* http://ccmixter.org/files/grapes/16626
