#!/bin/bash

echo "Starting application..."

echo "Exporting environment variables..."
export FLASK_APP=app

echo "Initiating database..."
flask db init
echo "Migrating database..."
flask db migrate
echo "Upgrading database..."
flask db upgrade

echo "Starting server..."
waitress-serve --port 5000 --call "app:create_app"

# Keep the container running
tail -f /dev/null
