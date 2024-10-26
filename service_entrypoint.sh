#!/bin/bash

# Wait for the database to be ready
export FLASK_APP=app
flask db init
flask db migrate
flask db upgrade

# Start the waitress server
waitress-serve --port 5000 --call "app:create_app"

# Keep the container running
tail -f /dev/null
