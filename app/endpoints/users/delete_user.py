from logging import getLogger
from sqlalchemy.engine.row import Row
from sqlalchemy.engine.base import Engine

from flask_restful import Resource
from flask_jwt_extended import jwt_required
from flask import request, make_response, jsonify

from app.resources.config import PROJECT_NAME
from app.resources.functions import get_db_engine
from app.resources.users_functions import get_verify_user_query, get_delete_user_query


logger = getLogger(f"{PROJECT_NAME}.delete_user_endpoint")


class DeleteUser(Resource):
	@jwt_required()
	def delete(self):
		logger.info("Getting request data...")
		email = request.json.get("email", None)

		logger.info("Checking request data...")
		if not email:
			raise KeyError("email")

		if not isinstance(email, str):
			raise TypeError("email")

		logger.info("Processing request...")
		logger.info("Connecting to DB...")
		engine: Engine = get_db_engine()

		logger.info("Verifying user existence...")
		query = get_verify_user_query(engine, email)

		with engine.connect() as connection:
			try:
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
			logger.info("Deleting record...")
			query = get_delete_user_query(engine, user_id)

			with engine.connect() as connection:
				with connection.begin() as transaction:
					connection.execute(query)
					connection.commit()
		except:
			transaction.rollback()
			raise Exception

		response: dict = {
			"status": "Success",
			"message": "User deleted successfully",
		}

		return make_response(jsonify(response), 200)