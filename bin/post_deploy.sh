#!/bin/bash
set -e

# Install Node.js dependencies via django-tailwind
echo "Installing Node.js dependencies..."
python manage.py tailwind install

# Compile Tailwind CSS
echo "Compiling Tailwind CSS..."
python manage.py tailwind build

# Execute database migrations
echo "Running database migrations..."
python manage.py migrate

echo "Post-deploy tasks completed successfully"

