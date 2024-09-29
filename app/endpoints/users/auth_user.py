from logging import getLogger
from datetime import timedelta
from sqlalchemy.engine.row import Row
from sqlalchemy.orm.query import Query
from sqlalchemy.engine.base import Engine

from flask_restful import Resource
from flask import request, make_response, jsonify
from flask_jwt_extended import create_access_token

from app.resources.functions import get_db_engine
from app.resources.config import PROJECT_NAME, GENERAL_ERROR_MESSAGE
from app.resources.users_functions import get_verify_user_query, decrypt


logger = getLogger(f"{PROJECT_NAME}.auth_user_endpoint")


class AuthUser(Resource):
	def post(self):
		logger.debug("Getting request data...")
		mail = request.json.get("mail", None)
		password = request.json.get("password", None)

		logger.debug("Checking request data...")
		if mail is None:
			logger.error("Missing request data field (mail). Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": "Missing request data field (mail)",
				"error_code": "TT.D400"
			}), 400)
		if password is None:
			logger.error("Missing request data field (password). Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": "Missing request data field (password)",
				"error_code": "TT.D400"
			}), 400)

		if not isinstance(mail, str):
			logger.error("Data field (mail) has the wrong data type (str). Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": "Data field (mail) has the wrong data type (str)",
				"error_code": "TT.D401"
			}), 400)
		if not isinstance(password, str):
			logger.error("Data field (password) has the wrong data type (str). Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": "Data field (password) has the wrong data type (str)",
				"error_code": "TT.D401"
			}), 400)

		logger.debug("Processing request...")
		logger.debug("Connecting to DB...")
		try:
			engine: Engine = get_db_engine()
		except Exception:
			logger.error("Error connecting to DB. Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": GENERAL_ERROR_MESSAGE,
				"error_code": "TT.500"
			}), 500)

		logger.debug("Creating query to verify user existence...")
		try:
			query: Query = get_verify_user_query(engine, mail, True)
		except Exception:
			logger.error("Error creating query to verify user existence. Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": GENERAL_ERROR_MESSAGE,
				"error_code": "TT.500"
			}), 500)

		logger.debug("Verifying user existence...")
		try:
			with engine.connect() as connection:
				user: Row | None = connection.execute(query).first()
		except Exception as e:
			logger.error(f"Error verifying user existence: {e}.\nAborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": GENERAL_ERROR_MESSAGE,
				"error_code": "TT.500"
			}), 500)

		if user is None:
			logger.error("Given user does not exist. Bad username or password error. Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": "Bad username or password",
				"error_code": "TT.D402"
			}), 401)
		else:
			logger.debug("Given user exists. Mapping user data...")
			user_data: dict = dict(user._mapping)

			logger.debug("Analysing password...")
			try:
				encrypted_password: bytes = decrypt(user_data["password"])
			except Exception:
				logger.error("Error decrypting password. Aborting request...")
				del encrypted_password
				del user_data["password"]

				return make_response(jsonify({
					"status": "Failed",
					"message": GENERAL_ERROR_MESSAGE,
					"error_code": "TT.500"
				}), 500)

			if encrypted_password != password:
				del encrypted_password
				del user_data["password"]

				logger.critical("Given user does not exist. Bad username or password error. Aborting request...")
				return make_response(jsonify({
					"status": "Failed",
					"message": "Bad username or password",
					"error_code": "TT.D402"
				}), 401)

			else:
				del encrypted_password
				del user_data["password"]

				logger.debug("Given user exists")
				logger.debug(f"Queried user data: {user_data}")

		logger.debug("Generating new JWT...")
		expires: timedelta = timedelta(days=1)
		access_token = create_access_token(identity=user_data, expires_delta=expires)

		logger.info("User authenticated successfully")
		return make_response(jsonify({
			"status": "Success",
			"token": access_token,
			"username": user_data["username"],
			"created_at": user_data["created_at"],
			"message": "User authenticated successfully",
		}), 200)
