from logging import getLogger

from flask_restful import Resource
from flask_jwt_extended import jwt_required
from flask import request, make_response, jsonify

from app.resources.config import PROJECT_NAME


logger = getLogger(f"{PROJECT_NAME}.speech_recognition_endpoint")


class SpeechRecognition(Resource):
	@jwt_required()
	def post(self) -> dict:
		logger.info("Getting request data...")
		# request_headers = request.headers
		audio_data = request.json.get("audio_data", None)

		logger.info("Checking request data...")
		if not audio_data:
			raise KeyError("audio_data")

		# if not isinstance(audio_data, str):
		# 	raise TypeError("audio_data")

		logger.info("Processing request...")
		print(audio_data)
		print(type(audio_data))

		response: dict = {
			"status": "Success",
			"message": "Data got successfully",
		}

		return make_response(jsonify(response), 200)