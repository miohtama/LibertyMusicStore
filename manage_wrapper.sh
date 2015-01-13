#!/bin/sh


# Fix py3.4 virtualenv can't find its own site-packages

. venv/bin/activate
python manage.py $@

