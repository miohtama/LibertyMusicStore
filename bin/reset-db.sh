#!/bin/bash
set -e
. venv/bin/activate
rm tatianastore.sqlite3
python manage.py syncdb --noinput && python manage.py migrate
echo "execfile('./bin/populate.py')" | python manage.py shell
