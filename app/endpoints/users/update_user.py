from logging import getLogger
from sqlalchemy.engine.row import Row
from sqlalchemy.orm.query import Query
from sqlalchemy.engine.base import Engine

from flask_restful import Resource
from flask_jwt_extended import jwt_required
from flask import request, make_response, jsonify

from app.resources.config import PROJECT_NAME
from app.resources.functions import get_db_engine
from app.resources.users_functions import (
	get_verify_user_query, get_update_user_query, encrypt
)


logger = getLogger(f"{PROJECT_NAME}.update_user_endpoint")


class UpdateUser(Resource):
	@jwt_required()
	def put(self):
		logger.info("Getting request data...")
		mail = request.json.get("mail", None)
		new_username = request.json.get("new_username", None)
		new_mail = request.json.get("new_mail", None)
		new_pwd = request.json.get("new_pwd", None)

		logger.info("Checking request data...")
		if not mail:
			raise KeyError("mail")

		if not isinstance(mail, str):
			raise TypeError("mail")

		logger.info("Processing request...")
		if new_pwd:
			logger.info("Encrypting new pwd...")
			new_pwd: bytes = encrypt(new_pwd)

		logger.info("Connecting to DB...")
		engine: Engine = get_db_engine()

		logger.info("Verifying user existence...")
		query: Query = get_verify_user_query(engine, mail)

		with engine.connect() as connection:
			try:
				with connection.begin() as transaction:
					user: Row | None = connection.execute(query).first()
			except:
				transaction.rollback()
				raise Exception

		if user is None:
			logger.error("Given user does not exist. Bad username or pwd error")
			raise KeyError("TT.D402")
		else:
			logger.info("Given user exists")
			user_id = dict(user._mapping)["id"]
			logger.info(f"User id found: {user_id}")

		logger.info("Updating record...")
		query = get_update_user_query(
			engine,
			user_id,
			new_username,
			new_mail,
			new_pwd
		)

		with engine.connect() as connection:
			try:
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
