from logging import getLogger
from sqlalchemy.engine.row import Row
from sqlalchemy.orm.query import Query
from sqlalchemy.engine.base import Engine

from flask_restful import Resource
from flask_jwt_extended import jwt_required
from flask import request, make_response, jsonify

from app.resources.functions import get_db_engine
from app.resources.places_functions import get_demo_data_query
from app.resources.config import PROJECT_NAME, GENERAL_ERROR_MESSAGE


logger = getLogger(f"{PROJECT_NAME}.get_all_records_endpoint")


class GetDemoData(Resource):
	@jwt_required()
	def get(self):
		logger.debug("Getting request data...")
		# request_headers = request.headers
		category = request.json.get("category", None)
		municipality = request.json.get("municipality", None)

		logger.debug("Checking request data...")
		if category is not None and not isinstance(category, str):
			logger.error("Data field (category) has the wrong data type (str). Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": "Data field (category) has the wrong data type (str)",
				"error_code": "TT.D401"
			}), 400)
		if municipality is not None and not isinstance(municipality, str):
			logger.error("Data field (municipality) has the wrong data type (str). Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": "Data field (municipality) has the wrong data type (str)",
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

		logger.debug("Creating query to get demo data...")
		try:
			query: Query = get_demo_data_query(engine, category, municipality)
		except Exception:
			logger.error("Error creating query to get demo data. Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": GENERAL_ERROR_MESSAGE,
				"error_code": "TT.500"
			}), 500)

		logger.debug("Making consult...")
		try:
			with engine.connect() as connection:
				data: list[Row] | None = connection.execute(query).fetchall()
		except Exception as e:
			logger.error(f"Error getting data: {e}.\nAborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": GENERAL_ERROR_MESSAGE,
				"error_code": "TT.500"
			}), 500)

		logger.debug("Checking data...")
		logger.debug(f"Gotten first 5 rows of data: {data[:5]}")
		if data is None:
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
