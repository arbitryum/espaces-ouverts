#!/bin/bash
set -e

# Compile Tailwind CSS
echo "Compiling Tailwind CSS..."
python manage.py tailwind build

# Execute database migrations
echo "Running database migrations..."
python manage.py migrate

echo "Post-deploy tasks completed successfully"

