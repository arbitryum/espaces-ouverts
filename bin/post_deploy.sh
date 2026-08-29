#!/bin/bash
set -e

# Execute database migrations
echo "Running database migrations..."
python manage.py migrate

# Collect static files for production
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "Post-deploy tasks completed successfully"

