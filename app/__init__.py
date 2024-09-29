import os
import logging
from vosk import SetLogLevel
from dotenv import load_dotenv

from flask_restful import Api
from flask.wrappers import Response
from flask import Flask, make_response, jsonify
from flask_jwt_extended import JWTManager, jwt_required

from app.resources.config import *

from app.endpoints.users.add_user import AddUser
from app.endpoints.users.auth_user import AuthUser
from app.endpoints.users.update_user import UpdateUser
from app.endpoints.users.delete_user import DeleteUser

from app.endpoints.data.get_record import GetRecord
from app.endpoints.data.get_demo_data import GetDemoData

from app.endpoints.models.agent import Agent
from app.endpoints.models.speech_recognition import SpeechRecognition


def create_app() -> Flask:
	###############################################################
	# Create application
	###############################################################
	app = Flask(__name__)
	api = Api(app)

	###############################################################
	# Set application configurations
	###############################################################
	# Flask configurations
	app.config["PROPAGATE_EXCEPTIONS"] = False

	# JWT configurations
	app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
	jwt = JWTManager(app)

	# logging configurations
	logging.basicConfig(level=logging.INFO, format=LOGGING_FORMAT)
	logger = logging.getLogger(PROJECT_NAME)

	# numba configurations
	numba_logger = logging.getLogger("numba")
	numba_logger.setLevel(logging.WARNING)

	# Load environment variables
	load_dotenv(DOTENV_ABSPATH)

	# vosk configuration
	SetLogLevel(-1)

	# librosa configurations
	os.environ["LIBROSA_CACHE_DIR"] = LIBROSA_CACHE_DIR

	###############################################################
	# Add routes (endpoints)
	###############################################################
	# Users endpoints
	api.add_resource(AddUser, "/add_user")
	api.add_resource(AuthUser, "/auth_user")
	api.add_resource(UpdateUser, "/update_user")
	api.add_resource(DeleteUser, "/delete_user")

	# Data endpoints
	api.add_resource(GetRecord, "/get_record")
	api.add_resource(GetDemoData, "/get_demo_data")

	# Models endpoints
	api.add_resource(Agent, "/agent")
	api.add_resource(SpeechRecognition, "/speech_recognition")

	@app.route('/')
	@jwt_required()
	def home() -> dict:
		""" Home route """
		response: dict = {
			"status": "Success",
			"message": "Welcome to Tip Trip. Hope this tool helps you to improve your travel experiences"
		}
		return make_response(jsonify(response), 200)

	###############################################################
	# Apply caching to all responses
	###############################################################
	@app.after_request
	def appy_caching(response: Response) -> Response:
		""" Apply caching to all responses """
		app.logger.info(app.logger)
		return response

	return app
