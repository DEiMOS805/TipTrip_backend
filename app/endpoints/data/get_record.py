from logging import getLogger
from sqlalchemy.engine.base import Engine

from flask_restful import Resource
from flask_jwt_extended import jwt_required
from flask import request, make_response, jsonify

from app.resources.config import PROJECT_NAME
from app.resources.functions import get_db_engine
from app.resources.places_functions import get_place_full_data_query


logger = getLogger(f"{PROJECT_NAME}.get_record_endpoint")


class GetRecord(Resource):
	@jwt_required()
	def get(self) -> dict:
		logger.info("Getting request data...")
		# request_headers = request.headers
		place_name = request.json.get("place_name", None)

		logger.info("Checking request data...")
		if not place_name:
			raise KeyError("place_name")

		if not isinstance(place_name, str):
			raise TypeError("place_name")

		logger.info("Processing request...")
		logger.info("Connecting to DB...")
		engine: Engine = get_db_engine()

		logger.info("Making consult...")
		query = get_place_full_data_query(engine, place_name)

		with engine.connect() as connection:
			data: list = connection.execute(query).fetchall()

		if data != []:
			logger.info("Mapping data...")
			data = [dict(row._mapping) for row in data]

			response: dict = {
				"status": "Success",
				"message": "Data got successfully",
				"data": data[0]
			}
		else:
			response: dict = {
				"status": "Success",
				"message": "Data not found for this place",
				"data": None
			}

		return make_response(jsonify(response), 200)
