from logging import getLogger
from sqlalchemy.engine.row import Row
from sqlalchemy.engine.base import Engine

from flask_restful import Resource
from flask_jwt_extended import jwt_required
from flask import request, make_response, jsonify

from app.resources.config import PROJECT_NAME
from app.resources.functions import (
	get_db_engine, get_verify_user_query, get_update_user_query
)


logger = getLogger(f"{PROJECT_NAME}.update_user_endpoint")


class UpdateUser(Resource):
	@jwt_required()
	def patch(self):
		logger.info("Getting request data...")
		email = request.json.get("email", None)
		new_username = request.json.get("new_username", None)
		new_email = request.json.get("new_email", None)
		new_password = request.json.get("new_password", None)
		new_role = request.json.get("new_role", None)
		new_image_path = request.json.get("new_image_path", None)

		logger.info("Checking request data...")
		if not email:
			raise KeyError("email")

		if not isinstance(email, str):
			raise TypeError("email")

		logger.info("Processing request...")
		logger.info("Connecting to DB...")
		engine: Engine = get_db_engine()

		try:
			logger.info("Verifying user existence...")
			query = get_verify_user_query(engine, email)

			with engine.connect() as connection:
				with connection.begin() as transaction:
					user: Row | None = connection.execute(query).first()
		except:
			transaction.rollback()
			raise Exception

		if user is None:
			logger.error("Given user does not exist. Bad username or password error")
			raise KeyError("TT.D402")
		else:
			logger.info("Given user exists")
			user_id = dict(user._mapping)["id"]
			logger.info(f"User id found: {user_id}")

		try:
			logger.info("Updating record...")
			query = get_update_user_query(
				engine,
				user_id,
				new_username,
				new_email,
				new_password,
				new_role,
				new_image_path
			)

			with engine.connect() as connection:
				with connection.begin() as transaction:
					connection.execute(query)
					connection.commit()
		except:
			transaction.rollback()
			raise Exception

		response: dict = {
			"status": "Success",
			"message": "User data updated successfully",
		}

		return make_response(jsonify(response), 201)