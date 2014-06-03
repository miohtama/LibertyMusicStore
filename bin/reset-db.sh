#!/bin/bash
. venv/bin/activate
rm tatianastore.sqlite3
python manage.py syncdb --noinput && python manage.py migrate
echo "execfile('./tatianastore/populate.py')" | python manage.py shell
