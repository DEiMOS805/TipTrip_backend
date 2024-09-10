import os
import logging
from vosk import SetLogLevel
from dotenv import load_dotenv

from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager

from app.resources.config import *


# Load environment variables
load_dotenv(DOTENV_ABSPATH)

# Create application
app = Flask(__name__)
api = Api(app)

# JWT configuration
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
jwt = JWTManager(app)

# Logging configuration
logging.basicConfig(level=logging.DEBUG, format=LOGGING_FORMAT)
logger = logging.getLogger(PROJECT_NAME)

numba_logger = logging.getLogger("numba")
numba_logger.setLevel(logging.WARNING)

# Set vosk log level
SetLogLevel(-1)

# Error handling
from app.resources.errors import *
