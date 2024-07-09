from logging import getLogger
from flask_restful import Resource
from flask import request, make_response, jsonify

from sqlalchemy import select, Table
from sqlalchemy.engine.base import Engine
from sqlalchemy.sql.schema import MetaData

from app import auth
from app.resources.functions import *
from app.resources.config import PROJECT_NAME, DB_DATA


logger = getLogger(f"{PROJECT_NAME}.get_record_endpoint")


class GetRecord(Resource):
	@auth.login_required
	def get(self) -> dict:
		logger.info("Getting request data...")
		# request_headers = request.headers
		request_data = request.get_json()

		logger.info("Checking request data...")
		if not "table_name" in request_data:
			raise TypeError("table_name")
		else:
			table_name = request_data["table_name"]

		if not isinstance(table_name, str):
			raise KeyError("table_name")

		if not "conditions" in request_data:
			raise TypeError("conditions")
		else:
			conditions = request_data["conditions"]

		if not isinstance(request_data["conditions"], dict):
			raise KeyError("conditions")

		#! CHECH THAT request_data["conditions"] IS NOT EMPTY

		logger.info("Processing request...")
		logger.info("Connecting to DB...")
		engine: Engine = get_db_engine(**DB_DATA)
		metadata: MetaData = get_db_metadata()

		try:
			logger.info("Connecting to table...")
			table = Table(table_name, metadata, autoload_with=engine)

			with engine.connect() as connection:
				with connection.begin() as transaction:
					logger.info("Making consult...")
					query = select(table)
					for column, value in conditions.items():
						query = query.where(table.c[column] == value)

					data: list = connection.execute(query).fetchall()

					# data = [list(row) for row in data]
					data = [dict(row._mapping) for row in data]
		except:
			transaction.rollback()
			raise Exception

		response: dict = {
			"status": "Correct",
			"data": data
		}

		return make_response(jsonify(response), 200)
