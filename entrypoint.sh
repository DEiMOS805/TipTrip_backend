#!/bin/bash

# Environment variables
export FLASK_APP=app

# Run database migrations
flask db init
flask db migrate
flask db upgrade

# Start the waitress server
waitress-serve --port 5000 --call "app:create_app"

# Keep the container running
tail -f /dev/null
