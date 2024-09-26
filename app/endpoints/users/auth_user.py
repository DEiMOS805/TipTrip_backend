from logging import getLogger
from datetime import timedelta
from sqlalchemy.engine.row import Row
from sqlalchemy.orm.query import Query
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
		mail = request.json.get("mail", None)
		pwd = request.json.get("pwd", None)

		logger.info("Checking request data...")
		if not mail:
			raise KeyError("mail")
		if not pwd:
			raise KeyError("pwd")

		if not isinstance(mail, str):
			raise TypeError("mail")
		if not isinstance(pwd, str):
			raise TypeError("pwd")

		logger.info("Processing request...")
		logger.info("Connecting to DB...")
		engine: Engine = get_db_engine()

		logger.info("Verifying user existence...")
		query: Query = get_verify_user_query(engine, mail, True)

		with engine.connect() as connection:
			user: Row | None = connection.execute(query).first()

		if user is None:
			logger.error("Given user does not exist. Bad username or password error")
			raise KeyError("TT.D402")
		else:
			user_data: dict = dict(user._mapping)
			if decrypt(user_data["pwd"]) != pwd:
				del user_data["pwd"]
				logger.error("Given user does not exist. Bad username or password error")
				raise KeyError("TT.D402")
			else:
				del user_data["pwd"]
				logger.info("Given user exists")
				logger.info(f"Queried user data: {user_data}")

		logger.info("Generating new JWT...")
		expires: timedelta = timedelta(days=1)
		access_token = create_access_token(identity=user_data, expires_delta=expires)
		response: dict = {
			"status": "Success",
			"token": access_token,
			"username": user_data["username"],
			"created_at": user_data["created_at"],
		}
		return make_response(jsonify(response), 200)
