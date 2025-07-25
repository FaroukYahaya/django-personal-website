#!/usr/bin/env bash
set -o errexit

echo "Installing requirements..."
pip install -r requirements.txt

echo "Making migrations..."
python manage.py makemigrations --noinput

echo "Applying migrations..."
python manage.py migrate --noinput

echo "Loading initial data..."
python manage.py loaddata working_data.json || echo "Data already exists or failed to load"

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Build completed successfully!"