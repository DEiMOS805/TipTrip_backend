from logging import getLogger
from sqlalchemy.exc import IntegrityError
from sqlalchemy.engine.base import Engine
from sqlalchemy.engine.cursor import CursorResult

from flask_restful import Resource
from flask import request, make_response, jsonify

from app.resources.config import PROJECT_NAME
from app.resources.functions import get_db_engine, get_add_user_query


logger = getLogger(f"{PROJECT_NAME}.add_user_endpoint")


class AddUser(Resource):
	def post(self):
		logger.info("Getting request data...")
		username = request.json.get("username", None)
		email = request.json.get("email", None)
		password = request.json.get("password", None)
		role = request.json.get("role", None)
		image_path = request.json.get("image_path", None)

		logger.info("Checking request data...")
		if not username:
			raise KeyError("username")
		if not email:
			raise KeyError("email")
		if not password:
			raise KeyError("password")

		if not isinstance(username, str):
			raise TypeError("username")
		if not isinstance(email, str):
			raise TypeError("email")
		if not isinstance(password, str):
			raise TypeError("password")

		logger.info("Processing request...")
		logger.info("Connecting to DB...")
		engine: Engine = get_db_engine()

		try:
			logger.info("Inserting record...")
			query = get_add_user_query(
				engine,
				username,
				email,
				password,
				role,
				image_path
			)

			with engine.connect() as connection:
				with connection.begin() as transaction:
					result: CursorResult = connection.execute(query)
					id: int = result.inserted_primary_key[0]
					connection.commit()

		except IntegrityError as e:
			transaction.rollback()
			raise IntegrityError(statement=None, params=None, orig=e)

		except:
			transaction.rollback()
			raise Exception

		response: dict = {
			"status": "Success",
			"message": "User created successfully",
			"id": id
		}

		return make_response(jsonify(response), 201)
