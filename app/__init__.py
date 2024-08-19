import os
import logging
from vosk import SetLogLevel
from dotenv import load_dotenv

from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager

from app.resources.config import *


load_dotenv(DOTENV_ABSPATH)
SetLogLevel(-1)

app = Flask(__name__)
api = Api(app)

app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
jwt = JWTManager(app)

logging.basicConfig(level=logging.DEBUG, format=LOGGING_FORMAT)
logger = logging.getLogger(PROJECT_NAME)

# Error handling
from app.resources.errors import *
