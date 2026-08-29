#!/bin/bash
set -e

# Start gunicorn server
gunicorn app.wsgi --log-file -
