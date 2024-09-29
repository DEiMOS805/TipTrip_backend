from logging import getLogger
from sqlalchemy.orm.query import Query
from sqlalchemy.engine.base import Engine

from flask_restful import Resource
from flask_jwt_extended import jwt_required
from flask import request, make_response, jsonify

from app.resources.functions import get_db_engine
from app.resources.places_functions import get_place_full_data_query
from app.resources.config import PROJECT_NAME, GENERAL_ERROR_MESSAGE


logger = getLogger(f"{PROJECT_NAME}.get_record_endpoint")


class GetRecord(Resource):
	@jwt_required()
	def get(self) -> dict:
		logger.debug("Getting request data...")
		place_name = request.json.get("place_name", None)

		logger.debug("Checking request data...")
		if place_name is None:
			logger.error("Missing request data field (place_name). Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": "Missing request data field (place_name)",
				"error_code": "TT.D400"
			}), 400)

		if not isinstance(place_name, str):
			logger.error("Data field (place_name) has the wrong data type (str). Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": "Data field (place_name) has the wrong data type (str)",
				"error_code": "TT.D401"
			}), 400)

		logger.debug("Processing request...")
		logger.debug("Connecting to DB...")
		try:
			engine: Engine = get_db_engine()
		except Exception:
			logger.error("Error connecting to DB. Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": GENERAL_ERROR_MESSAGE,
				"error_code": "TT.500"
			}), 500)

		logger.debug("Creating query to get full place data...")
		try:
			query: Query = get_place_full_data_query(engine, place_name)
		except Exception:
			logger.error("Error creating query to get full place data. Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": GENERAL_ERROR_MESSAGE,
				"error_code": "TT.500"
			}), 500)

		logger.debug("Making consult...")
		try:
			with engine.connect() as connection:
				data: list = connection.execute(query).fetchall()
		except Exception as e:
			logger.error(f"Error making consult to get full place data: {e}.\nAborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": GENERAL_ERROR_MESSAGE,
				"error_code": "TT.500"
			}), 500)

		logger.debug("Checking data...")
		logger.debug(f"Gotten data: {data}")
		if data == []:
			logger.info("Request completed successfully but no data found")
			return make_response(jsonify({
				"status": "Success",
				"message": "No data found"
			}), 204)
		else:
			logger.debug("Mapping data...")
			data = [dict(row._mapping) for row in data]

			logger.info("Request completed successfully")
			return make_response(jsonify({
				"status": "Success",
				"message": "Data got successfully",
				"data": data
			}), 200)
