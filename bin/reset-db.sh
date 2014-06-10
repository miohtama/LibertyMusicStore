#!/bin/bash
. venv/bin/activate
rm tatianastore.sqlite3 > /dev/null 2>&1
set -e
python manage.py syncdb --noinput && python manage.py migrate
echo "execfile('./bin/populate.py')" | python manage.py shell
