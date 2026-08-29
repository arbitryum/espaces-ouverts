#!/bin/bash
set -e

# Collect static files (this will warn if source dir doesn't exist, but won't fail)
python manage.py collectstatic --noinput --clear || true

# Start gunicorn server
gunicorn app.wsgi --log-file -

