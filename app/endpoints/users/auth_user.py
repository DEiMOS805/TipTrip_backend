from logging import getLogger
from datetime import timedelta
from sqlalchemy.engine.row import Row
from sqlalchemy.engine.base import Engine

from flask_restful import Resource
from flask import request, make_response, jsonify
from flask_jwt_extended import create_access_token

from app.resources.config import PROJECT_NAME
from app.resources.functions import get_db_engine
from app.resources.users_functions import get_verify_user_query, decrypt


logger = getLogger(f"{PROJECT_NAME}.auth_user_endpoint")


class AuthUser(Resource):
	def post(self):
		logger.info("Getting request data...")
		email = request.json.get("email", None)
		password = request.json.get("password", None)

		logger.info("Checking request data...")
		if not email:
			raise KeyError("email")
		if not password:
			raise KeyError("password")

		if not isinstance(email, str):
			raise TypeError("email")
		if not isinstance(password, str):
			raise TypeError("password")

		logger.info("Processing request...")
		logger.info("Connecting to DB...")
		engine: Engine = get_db_engine()

		logger.info("Verifying user existence...")
		query = get_verify_user_query(engine, email, True)

		with engine.connect() as connection:
			user: Row | None = connection.execute(query).first()

		if user is None:
			logger.error("Given user does not exist. Bad username or password error")
			raise KeyError("TT.D402")
		else:
			user_data: dict = dict(user._mapping)
			if decrypt(user_data["contraseña"]) != password:
				logger.error("Given user does not exist. Bad username or password error")
				raise KeyError("TT.D402")
			else:
				del user_data["contraseña"]
				logger.info("Given user exists")
				logger.info(f"Queried user data: {user_data}")

		logger.info("Generating new JWT...")
		expires: timedelta = timedelta(days=1)
		access_token = create_access_token(identity=user_data, expires_delta=expires)
		response: dict = {
			"status": "Success",
			"token": access_token,
		}
		return make_response(jsonify(response), 200)
