import logging
from logging import Logger
from vosk import SetLogLevel
from os import getenv, environ
from dotenv import load_dotenv

from flasgger import Swagger
from flask_restful import Api
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask.wrappers import Response as WrapperResponse
from flask import Flask, Response, make_response, jsonify

from werkzeug.exceptions import HTTPException
from jwt.exceptions import ExpiredSignatureError, InvalidSignatureError
from flask_jwt_extended.exceptions import NoAuthorizationError, InvalidHeaderError, RevokedTokenError, UserLookupError

from app.resources.config import *
from app.resources.database import db
from app.resources.swagger_template import swagger_template
# from app.resources.error_handlers import set_error_handlers

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
	############################ Set error handlers ###########################
	###########################################################################

	# set_error_handlers(app, jwt)

	@jwt.unauthorized_loader
	def handle_unauthorized_token(e) -> Response:
		return make_response(jsonify({
			"status": "Failed",
			"message": "Unauthorized token",
			"error_code": "TT.401"
		}), 401)

	@app.errorhandler(HTTPException)
	def not_found_error_handler(error: HTTPException) -> Response:
		""" Function that handles the error 404 """
		return make_response(jsonify({
			"status": "Failed",
			"message": "Resource not found",
			"error_code": "TT.404"
		}), 404)

	@app.errorhandler(ExpiredSignatureError)
	def handle_expired_token(error: ExpiredSignatureError) -> Response:
		return make_response(jsonify({
			"status": "Failed",
			"message": "Token already expired",
			"error_code": "TT.401"
		}), 401)

	@app.errorhandler(InvalidSignatureError)
	def handle_invalid_signature(error: InvalidSignatureError) -> Response:
		return make_response(jsonify({
			"status": "Failed",
			"message": "Invalid token signature",
			"error_code": "TT.401"
		}), 401)

	@app.errorhandler(InvalidHeaderError)
	def handle_invalid_token(error: InvalidHeaderError) -> Response:
		return make_response(jsonify({
			"status": "Failed",
			"message": "Invalid token",
			"error_code": "TT.401"
		}), 401)

	@app.errorhandler(NoAuthorizationError)
	def handle_missing_token(error: NoAuthorizationError) -> Response:
		return make_response(jsonify({
			"status": "Failed",
			"message": "Missing token",
			"error_code": "TT.401"
		}), 401)

	@app.errorhandler(RevokedTokenError)
	def handle_revoked_token(error: RevokedTokenError) -> Response:
		return make_response(jsonify({
			"status": "Failed",
			"message": "Token revoked",
			"error_code": "TT.401"
		}), 401)

	@app.errorhandler(UserLookupError)
	def handle_user_lookup_error(error: UserLookupError) -> Response:
		return make_response(jsonify({
			"status": "Failed",
			"message": "User not found",
			"error_code": "TT.404"
		}), 404)

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
