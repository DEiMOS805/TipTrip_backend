from logging import getLogger
from sqlalchemy.orm.query import Query
from sqlalchemy.engine.base import Engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.engine.cursor import CursorResult

from flask_restful import Resource
from flask import request, make_response, jsonify

from app.resources.functions import get_db_engine
from app.resources.config import PROJECT_NAME, GENERAL_ERROR_MESSAGE
from app.resources.users_functions import get_add_user_query, encrypt


logger = getLogger(f"{PROJECT_NAME}.add_user_endpoint")


class AddUser(Resource):
	def post(self):
		logger.debug("Getting request data...")
		username = request.json.get("username", None)
		mail = request.json.get("mail", None)
		password = request.json.get("password", None)

		logger.debug("Checking request data...")
		if username is None:
			logger.error("Missing request data field (username). Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": "Missing request data field (username)",
				"error_code": "TT.D400"
			}), 400)
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

		if not isinstance(username, str):
			logger.error("Data field (username) has the wrong data type (str). Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": "Data field (username) has the wrong data type (str)",
				"error_code": "TT.D401"
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
		logger.debug("Encrypting password...")
		try:
			password: bytes = encrypt(password)
		except Exception:
			logger.error("Error encrypting password. Aborting request...")
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

		logger.debug("Creating query...")
		try:
			query: Query = get_add_user_query(engine, username, mail, password)
		except Exception:
			logger.error("Error creating query. Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": GENERAL_ERROR_MESSAGE,
				"error_code": "TT.500"
			}), 500)

		logger.debug("Inserting record...")
		try:
			with engine.connect() as connection:
				with connection.begin() as transaction:
					try:
						result: CursorResult = connection.execute(query)
						id: int = result.inserted_primary_key[0]
						connection.commit()
					except IntegrityError:
						logger.error("Email already exists in db. Aborting request...")
						transaction.rollback()
						return make_response(jsonify({
							"status": "Failed",
							"message": "Email already exists in db",
							"error_code": "TT.D409"
						}), 409)
					except Exception as e:
						transaction.rollback()
						logger.error(f"Error inserting record {e}.\nAborting request...")
						return make_response(jsonify({
							"status": "Failed",
							"message": GENERAL_ERROR_MESSAGE,
							"error_code": "TT.500"
						}), 500)
		except Exception as e:
			logger.error(f"Error connecting with DB to make the transaction: {e}.\nAborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": GENERAL_ERROR_MESSAGE,
				"error_code": "TT.500"
			}), 500)

		logger.info("User created successfully")
		return make_response(jsonify({
			"status": "Success",
			"message": "User created successfully",
			"id": id
		}), 201)
