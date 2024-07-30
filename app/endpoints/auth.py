from logging import getLogger
from sqlalchemy.engine.row import Row
from sqlalchemy.engine.base import Engine

from flask_restful import Resource
from flask import request, make_response, jsonify
from flask_jwt_extended import create_access_token

# from app import auth
from app.resources.config import PROJECT_NAME
from app.resources.functions import get_db_engine, get_verify_user_query


logger = getLogger(f"{PROJECT_NAME}.auths")


class Auth(Resource):
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

		try:
			logger.info("Making consult...")
			query = get_verify_user_query(engine, email, password)

			with engine.connect() as connection:
				with connection.begin() as transaction:
					user: Row | None = connection.execute(query).first()

		except:
			transaction.rollback()
			raise Exception

		if user is None:
			response: dict = {
				"status": "Failed",
				"message": "Bad username or password"
			}
			return make_response(jsonify(response), 401)
		else:
			user_data: dict = dict(user._mapping)
			logger.info(f"Queried user data: {user_data}")

		access_token = create_access_token(identity=user_data["id"])
		response: dict = {
			"status": "Correct",
			"token": access_token,
			"user_id": user_data["id"]
		}
		return make_response(jsonify(response), 200)
