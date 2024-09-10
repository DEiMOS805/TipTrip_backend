from logging import getLogger
from sqlalchemy.engine.base import Engine

from flask_restful import Resource
from flask_jwt_extended import jwt_required
from flask import request, make_response, jsonify

from app.resources.config import PROJECT_NAME
from app.resources.functions import get_db_engine
from app.resources.places_functions import get_demo_data_query


logger = getLogger(f"{PROJECT_NAME}.get_all_records_endpoint")


class GetDemoData(Resource):
	@jwt_required()
	def get(self):
		logger.info("Getting request data...")
		# request_headers = request.headers
		category = request.json.get("category", None)
		municipality = request.json.get("municipality", None)

		logger.info("Checking request data...")
		if category is not None and not isinstance(category, str):
			raise TypeError("category")
		if municipality is not None and not isinstance(municipality, str):
			raise TypeError("municipality")

		logger.info("Processing request...")
		logger.info("Connecting to DB...")
		engine: Engine = get_db_engine()

		logger.info("Making consult...")
		query = get_demo_data_query(engine, category, municipality)

		with engine.connect() as connection:
			data: list = connection.execute(query).fetchall()

		logger.info("Mapping data...")
		data = [dict(row._mapping) for row in data]

		response: dict = {
			"status": "Success",
			"message": "Data got successfully",
			"data": data
		}

		return make_response(jsonify(response), 200)
