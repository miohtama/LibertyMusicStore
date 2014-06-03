#!/bin/bash
. venv/bin/activate
pkill -f manage.py
pkill -f uwsgi
nohup python manage.py run_huey > logs/huey.log &
sleep 1
uwsgi uwsgi.prod.ini

