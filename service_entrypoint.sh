#!/bin/bash

waitress-serve --port 5000 --call "app:create_app"

tail -f /dev/null