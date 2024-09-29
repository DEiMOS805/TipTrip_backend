from logging import getLogger
from sqlalchemy.engine.row import Row
from sqlalchemy.orm.query import Query
from sqlalchemy.engine.base import Engine

from flask_restful import Resource
from flask_jwt_extended import jwt_required
from flask import request, make_response, jsonify

from app.resources.functions import get_db_engine
from app.resources.users_functions import (
	get_verify_user_query, get_update_user_query, encrypt)
from app.resources.config import PROJECT_NAME, GENERAL_ERROR_MESSAGE


logger = getLogger(f"{PROJECT_NAME}.update_user_endpoint")


class UpdateUser(Resource):
	@jwt_required()
	def put(self):
		logger.debug("Getting request data...")
		mail = request.json.get("mail", None)
		new_username = request.json.get("new_username", None)
		new_mail = request.json.get("new_mail", None)
		new_password = request.json.get("new_password", None)

		logger.debug("Checking request data...")
		if mail is None:
			logger.error("Missing request data field (mail). Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": "Missing request data field (mail)",
				"error_code": "TT.D400"
			}), 400)

		if not isinstance(mail, str):
			logger.error("Data field (mail) has the wrong data type (str). Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": "Data field (mail) has the wrong data type (str)",
				"error_code": "TT.D401"
			}), 400)

		logger.debug("Processing request...")
		if new_password:
			logger.debug("Encrypting new pwd...")
			try:
				new_password: bytes = encrypt(new_password)
			except Exception:
				logger.error("Error encrypting new password. Aborting request...")
				return make_response(jsonify({
					"status": "Failed",
					"message": GENERAL_ERROR_MESSAGE,
					"error_code": "TT.500"
				}), 500)

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
			query: Query = get_verify_user_query(engine, mail)
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
		except Exception:
			logger.error("Error executing query. Aborting request...")
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
			logger.debug("Given user exists")
			user_id = dict(user._mapping)["id"]
			logger.debug(f"User id found: {user_id}")

		logger.debug("Creating query to delete user...")
		try:
			query = get_update_user_query(
				engine, user_id, new_username, new_mail, new_password)
		except Exception:
			logger.error("Error creating query to update user. Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": GENERAL_ERROR_MESSAGE,
				"error_code": "TT.500"
			}), 500)

		logger.debug("Updating record...")
		try:
			with engine.connect() as connection:
				with connection.begin() as transaction:
					try:
						connection.execute(query)
						connection.commit()
					except Exception as e:
						transaction.rollback()
						logger.error(f"Error updating record {e}.\nAborting request...")
						return make_response(jsonify({
							"status": "Failed",
							"message": GENERAL_ERROR_MESSAGE,
							"error_code": "TT.500"
						}), 500)
		except Exception as e:
			logger.error(f"Error updating record: {e}.\nAborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": GENERAL_ERROR_MESSAGE,
				"error_code": "TT.500"
			}), 500)

		logger.debug("User data updated successfully")
		return make_response(jsonify({
			"status": "Success",
			"message": "User data updated successfully",
		}), 201)
