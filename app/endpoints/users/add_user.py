from logging import getLogger
from sqlalchemy.orm.query import Query
from sqlalchemy.engine.base import Engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.engine.cursor import CursorResult

from flask_restful import Resource
from flask import request, make_response, jsonify

from app.resources.config import PROJECT_NAME
from app.resources.functions import get_db_engine
from app.resources.users_functions import get_add_user_query, encrypt


logger = getLogger(f"{PROJECT_NAME}.add_user_endpoint")


class AddUser(Resource):
	def post(self):
		logger.info("Getting request data...")
		username = request.json.get("username", None)
		mail = request.json.get("mail", None)
		pwd = request.json.get("pwd", None)

		logger.info("Checking request data...")
		if not username:
			raise KeyError("username")
		if not mail:
			raise KeyError("mail")
		if not pwd:
			raise KeyError("pwd")

		if not isinstance(username, str):
			raise TypeError("username")
		if not isinstance(mail, str):
			raise TypeError("mail")
		if not isinstance(pwd, str):
			raise TypeError("pwd")

		logger.info("Processing request...")
		logger.info("Encrypting pwd...")
		pwd: bytes = encrypt(pwd)

		logger.info("Connecting to DB...")
		engine: Engine = get_db_engine()

		logger.info("Inserting record...")
		query: Query = get_add_user_query(
			engine,
			username,
			mail,
			pwd
		)

		with engine.connect() as connection:
			try:
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
