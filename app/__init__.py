import logging
from logging import Logger
from vosk import SetLogLevel
from os import getenv, environ
from dotenv import load_dotenv

from flasgger import Swagger
from flask_restful import Api
from flask_migrate import Migrate
from flask.wrappers import Response as WrapperResponse
from flask_jwt_extended import JWTManager, jwt_required
from flask import Flask, Response, make_response, jsonify

from app.resources.config import *
from app.resources.database import db
from app.blueprints.user import user_blueprint
from app.blueprints.place import place_blueprint
from app.blueprints.models import model_blueprint
from app.resources.swagger_template import swagger_template


load_dotenv(DOTENV_ABSPATH)


def create_app() -> Flask:
	###########################################################################
	######################### Create application ##############################
	###########################################################################

	app = Flask(__name__)
	api = Api(app)

	###########################################################################
	#################### Set application configurations #######################
	###########################################################################

	# Database configurations
	app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DB_URL")
	app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
	db.init_app(app)
	migrate = Migrate(app, db)

	# Swagger configurations
	swagger: Swagger = Swagger(app, template=swagger_template)

	# Flask configurations
	app.config["PROPAGATE_EXCEPTIONS"] = False

	# JWT configurations
	app.config["JWT_SECRET_KEY"] = getenv("JWT_SECRET_KEY")
	jwt = JWTManager(app)

	# logging configurations
	logging.basicConfig(level=logging.DEBUG, format=LOGGING_FORMAT)
	logger: Logger = logging.getLogger(PROJECT_NAME)

	# numba configurations
	numba_logger: Logger = logging.getLogger("numba")
	numba_logger.setLevel(logging.WARNING)

	# vosk configuration
	SetLogLevel(-1)

	# librosa configurations
	environ["LIBROSA_CACHE_DIR"] = LIBROSA_CACHE_DIR

	###########################################################################
	######################### Set JWT error handlers ##########################
	###########################################################################

	@jwt.expired_token_loader
	def handle_expired_token(jwt_header, jwt_payload) -> Response:
		return make_response(jsonify({
			"status": "Failed",
			"message": "Token already expired",
			"error_code": "TT.401"
		}), 401)

	@jwt.invalid_token_loader
	def handle_invalid_token(e) -> Response:
		return make_response(jsonify({
			"status": "Failed",
			"message": "Invalid token",
			"error_code": "TT.422"
		}), 422)

	@jwt.unauthorized_loader
	def handle_missing_token(e) -> Response:
		return make_response(jsonify({
			"status": "Failed",
			"message": "Missing or unauthorized token",
			"error_code": "TT.401"
		}), 401)

	###########################################################################
	####################### Add routes and blueprints #########################
	###########################################################################

	app.register_blueprint(user_blueprint, url_prefix="/users")
	app.register_blueprint(place_blueprint, url_prefix="/places")
	app.register_blueprint(model_blueprint, url_prefix="/models")


	@app.route('/')
	@jwt_required()
	def home() -> Response:
		return make_response(jsonify({
			"status": "Success",
			"message": "Welcome to Tip Trip. Hope this tool helps you to improve your travel experiences"
		}), 200)


	###########################################################################
	###################### Apply caching to all responses #####################
	###########################################################################
	@app.after_request
	def appy_caching(response: WrapperResponse) -> WrapperResponse:
		""" Apply caching to all responses """
		app.logger.info(app.logger)
		return response

	return app
