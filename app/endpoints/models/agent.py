from os import remove
from os.path import join
from logging import getLogger

from flask_restful import Resource
from flask_jwt_extended import jwt_required
from flask import request, make_response, jsonify

from app.resources.config import PROJECT_NAME
from app.resources.models_functions import tts_func


logger = getLogger(f"{PROJECT_NAME}.agent_endpoint")


class Agent(Resource):
	@jwt_required()
	def post(self) -> dict:
		logger.info("Getting request data...")
		# request_headers = request.headers
		prompt = request.json.get("prompt", None)

		logger.info("Checking request data...")
		if not prompt:
			raise KeyError("prompt")

		if not isinstance(prompt, str):
			raise TypeError("prompt")

		logger.info(f"Received prompt: {prompt}")

		logger.info("Processing request...")
		audio_data = tts_func(prompt)

		response: dict = {
			"status": "Success",
			"message": "Agent response completed successfully",
			"audio_data": audio_data
		}

		return make_response(jsonify(response), 200)
