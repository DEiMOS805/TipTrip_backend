from os import remove
from os.path import join
from base64 import b64decode
from logging import getLogger

from flask_restful import Resource
from flask_jwt_extended import jwt_required
from flask import request, make_response, jsonify

from app.resources.models_functions import speech_recognition
from app.resources.config import PROJECT_NAME, TEMP_FILE_NAME, GENERAL_ERROR_MESSAGE


logger = getLogger(f"{PROJECT_NAME}.speech_recognition_endpoint")


class SpeechRecognition(Resource):
	@jwt_required()
	def post(self) -> dict:
		logger.info("Getting request data...")
		audio_data = request.json.get("audio_data", None)

		logger.info("Checking request data...")
		if audio_data is None:
			logger.error("Missing request data field (audio_data). Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": "Missing request data field (audio_data)",
				"error_code": "TT.D400"
			}), 400)

		if not isinstance(audio_data, str):
			logger.error("Data field (audio_data) has the wrong data type (str). Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": "Data field (audio_data) has the wrong data type (str)",
				"error_code": "TT.D401"
			}), 400)

		logger.info("Processing request...")
		logger.info("Decoding audio data...")
		try:
			audio_data: bytes = b64decode(audio_data)
		except Exception:
			logger.error("Error decoding audio data. Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": "Error decoding audio data",
				"error_code": "TT.500"
			}), 500)

		logger.info("Saving audio data as a temporary file...")
		try:
			with open(join("/tmp", TEMP_FILE_NAME), "wb") as file:
				file.write(audio_data)
		except Exception:
			logger.error("Error saving audio data as a temporary file. Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": GENERAL_ERROR_MESSAGE,
				"error_code": "TT.500"
			}), 500)

		logger.info("Starting speech recognition...")
		try:
			text: str = speech_recognition()
		except Exception:
			logger.error("Error during speech recognition process. Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": GENERAL_ERROR_MESSAGE,
				"error_code": "TT.500"
			}), 500)

		logger.info("Deleting audio file...")
		try:
			remove(join("/tmp", TEMP_FILE_NAME))
		except Exception:
			logger.error("Error deleting audio file. Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": GENERAL_ERROR_MESSAGE,
				"error_code": "TT.500"
			}), 500)

		logger.info("Speech recognition process completed successfully")
		return make_response(jsonify({
			"status": "Success",
			"message": "Speech recognition process completed successfully",
			"text": text
		}), 200)
