#!/bin/bash
set -e

# Execute database migrations
python manage.py migrate

echo "Post-deploy tasks completed successfully"
