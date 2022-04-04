#!/bin/sh

python manage.py migrate&&python manage.py collectstatic --noinput&&/usr/local/bin/gunicorn Argminer.wsgi:application --reload -w 1 -b :8000

