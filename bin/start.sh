#!/bin/bash
set -e

# Collect static files
python manage.py collectstatic --noinput

# Start gunicorn server
gunicorn app.wsgi --log-file -
