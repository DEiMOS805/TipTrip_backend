from os import remove
from os.path import join
from base64 import b64decode
from logging import getLogger

from flask_restful import Resource
from flask_jwt_extended import jwt_required
from flask import request, make_response, jsonify

from app.resources.functions import save_as_temp_file
from app.resources.models_functions import speech_recognition
from app.resources.config import PROJECT_NAME, TEMP_ABSPATH, TEMP_FILE_NAME


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

		if not isinstance(audio_data, str):
			raise TypeError("audio_data")

		logger.info("Processing request...")
		logger.info("Decoding audio data...")
		audio_data = b64decode(audio_data)

		logger.info("Saving audio data as a temporary file...")
		save_as_temp_file(audio_data)

		logger.info("Starting speech recognition...")
		text: str = speech_recognition()

		logger.info("Deleting audio file...")
		remove(join(TEMP_ABSPATH, TEMP_FILE_NAME))

		response: dict = {
			"status": "Success",
			"message": "Speech recognition completed successfully",
			"text": text
		}

		return make_response(jsonify(response), 200)