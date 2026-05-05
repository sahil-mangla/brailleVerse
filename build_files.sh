#!/usr/bin/env bash
# Build script for Vercel - collects static files

set -o errexit

echo "Installing dependencies..."
pip install -r requirements.txt --break-system-packages

echo "Collecting static files..."
python manage.py collectstatic --no-input --clear

echo "Build complete!"
