import logging

from flask import Flask
from flask_restful import Api
from flask_httpauth import HTTPBasicAuth

from app.resources.config import PROJECT_NAME, LOGGING_FORMAT


app = Flask(__name__)
api = Api(app)

auth = HTTPBasicAuth()

logging.basicConfig(level=logging.DEBUG, format=LOGGING_FORMAT)
logger = logging.getLogger(PROJECT_NAME)

# Error handling
from app.resources.errors import *
