from logging import getLogger

from flask_restful import Resource
from flask_jwt_extended import jwt_required
from flask import request, make_response, jsonify

from app.resources.models_functions import tts_func
from app.resources.config import PROJECT_NAME, GENERAL_ERROR_MESSAGE


logger = getLogger(f"{PROJECT_NAME}.agent_endpoint")


class Agent(Resource):
	@jwt_required()
	def post(self) -> dict:
		logger.debug("Getting request data...")
		prompt = request.json.get("prompt", None)

		logger.debug("Checking request data...")
		if prompt is None:
			logger.error("Missing request data field (prompt). Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": "Missing request data field (prompt)",
				"error_code": "TT.D400"
			}), 400)

		if not isinstance(prompt, str):
			logger.error("Data field (prompt) has the wrong data type (str). Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": "Data field (prompt) has the wrong data type (str)",
				"error_code": "TT.D401"
			}), 400)

		logger.debug(f"Received prompt: {prompt}")

		logger.debug("Processing request...")
		logger.debug("Generating agent response...")
		try:
			audio_data: dict = tts_func(prompt)
		except Exception as e:
			logger.error(f"Error generating agent response {e}.\nAborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": GENERAL_ERROR_MESSAGE,
				"error_code": "TT.500"
			}), 500)

		logger.info("Agent response process completed successfully")
		return make_response(jsonify({
			"status": "Success",
			"message": "Agent response process completed successfully",
			"audio_data": audio_data
		}), 200)
