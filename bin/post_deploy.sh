#!/bin/bash
set -e

# Install Node.js dependencies for Tailwind CSS
echo "Installing Node.js dependencies..."
if [ -d "theme/static_src" ]; then
    cd theme/static_src && npm install && cd - > /dev/null
fi

# Compile Tailwind CSS
echo "Compiling Tailwind CSS..."
python manage.py tailwind build

# Execute database migrations
echo "Running database migrations..."
python manage.py migrate

echo "Post-deploy tasks completed successfully"

