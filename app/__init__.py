import logging
from logging import Logger
from vosk import SetLogLevel
from os import getenv, environ
from dotenv import load_dotenv
from langchain.globals import set_debug

from flasgger import Swagger
from flask_restful import Api
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from werkzeug.exceptions import HTTPException
from flask.wrappers import Response as WrapperResponse
from flask import Flask, Response, make_response, jsonify

from app.resources.config import *
from app.resources.database import db
from app.resources.swagger_template import swagger_template

from app.endpoints.home import Home
from app.endpoints.download import Download
from app.endpoints.blueprints.user import user_blueprint
from app.endpoints.blueprints.place import place_blueprint
from app.endpoints.blueprints.models import model_blueprint


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
	app.config["PROPAGATE_EXCEPTIONS"] = True

	# JWT configurations
	app.config["JWT_SECRET_KEY"] = getenv("JWT_SECRET_KEY")
	jwt = JWTManager(app)

	# logging configurations
	logging.basicConfig(level=logging.DEBUG, format=LOGGING_FORMAT)
	logger: Logger = logging.getLogger(PROJECT_NAME)

	# numba configurations
	numba_logger: Logger = logging.getLogger("numba")
	numba_logger.setLevel(logging.WARNING)

	# Langchain configurations
	set_debug(False)

	# vosk configuration
	SetLogLevel(-1)

	# librosa configurations
	environ["LIBROSA_CACHE_DIR"] = LIBROSA_CACHE_DIR

	###########################################################################
	############################ Set error handlers ###########################
	###########################################################################

	@app.errorhandler(HTTPException)
	def not_found_error_handler(error: HTTPException) -> Response:
		return make_response(jsonify({
			"status": "Failed",
			"message": "Resource not found"
		}), 404)

	@jwt.unauthorized_loader
	def unauthorized_loader_error_handler(reason) -> Response:
		return make_response(jsonify({
			"status": "Failed",
			"message": reason
		}), 401)

	@jwt.expired_token_loader
	def expired_token_error_handler(jwt_header, jwt_payload) -> Response:
		return make_response(jsonify({
			"status": "Failed",
			"message": "Token has expired"
		}), 401)

	@jwt.invalid_token_loader
	def invalid_token_error_handler(error) -> Response:
		return make_response(jsonify({
			"status": "Failed",
			"message": "Invalid token"
		}), 401)

	@jwt.revoked_token_loader
	def revoked_token_error_handler(jwt_header, jwt_payload) -> Response:
		return make_response(jsonify({
			"status": "Failed",
			"message": "Token has been revoked"
		}), 401)

	###########################################################################
	####################### Add routes and blueprints #########################
	###########################################################################

	api.add_resource(Home, '/')
	api.add_resource(Download, "/download/<string:os>")

	app.register_blueprint(user_blueprint, url_prefix="/users")
	app.register_blueprint(place_blueprint, url_prefix="/places")
	app.register_blueprint(model_blueprint, url_prefix="/models")

	###########################################################################
	###################### Apply caching to all responses #####################
	###########################################################################
	@app.after_request
	def appy_caching(response: WrapperResponse) -> WrapperResponse:
		""" Apply caching to all responses """
		app.logger.info(app.logger)
		return response

	return app
