#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py migrate
python manage.py setup_healthconnect
python manage.py collectstatic --noinput
