from os import remove
from os.path import join
from base64 import b64decode
from logging import Logger, getLogger
from flask_restful import Api, Resource
from flask_jwt_extended import jwt_required
from flask_restful.reqparse import Namespace
from flask import Blueprint, Response, make_response, jsonify

from app.resources.config import *
from app.resources.functions import speech_recognition, consultar_agente, tts_func
from app.resources.parsers import create_speech_recognition_model_parser, create_agent_model_parser


logger: Logger = getLogger(f"{PROJECT_NAME}.model_blueprint")

model_blueprint: Blueprint = Blueprint("model", __name__)
api: Api = Api(model_blueprint)


class SpeechRecognition(Resource):
	@jwt_required()
	def post(self) -> Response:
		logger.debug("Starting speech recognition process...")

		logger.debug("Checking request data...")
		args: Namespace = create_speech_recognition_model_parser()

		logger.debug("Decoding audio data...")
		try:
			audio: bytes = b64decode(args["audio"])

		except Exception as e:
			logger.error(f"Error decoding audio data: {e}. Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": GENERAL_ERROR_MESSAGE,
				"error_code": "TT.500"
			}), 500)

		logger.debug("Saving audio data as a temp file...")
		try:
			with open(join("/tmp", TEMP_FILE_NAME), "wb") as file:
				file.write(audio)

		except Exception:
			logger.error("Error saving audio data as a temp file. Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": GENERAL_ERROR_MESSAGE,
				"error_code": "TT.500"
			}), 500)

		logger.debug("Processing audio data with model...")
		try:
			text: str = speech_recognition()

		except Exception as e:
			logger.error(f"Error during speech recognition process: {e}. Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": GENERAL_ERROR_MESSAGE,
				"error_code": "TT.500"
			}), 500)

		logger.info("Deleting temp audio file...")
		try:
			remove(join("/tmp", TEMP_FILE_NAME))

		except Exception as e:
			logger.error(f"Error deleting audio file: {e}. Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": GENERAL_ERROR_MESSAGE,
				"error_code": "TT.500"
			}), 500)

		logger.info("Return successfull response...")
		return make_response(jsonify({
			"status": "Success",
			"message": "Speech recognition process completed successfully",
			"text": text
		}), 201)


class Agent(Resource):
	@jwt_required()
	def post(self) -> Response:
		logger.debug("Starting agent process...")

		logger.debug("Checking request data...")
		args: Namespace = create_agent_model_parser()

		logger.debug("Procesing prompt with agent model...")
		try:
			result: dict = {
				"text": consultar_agente(args["prompt"])
			}

		except Exception as e:
			logger.error(f"Error generating agent response {e}.\nAborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": GENERAL_ERROR_MESSAGE,
				"error_code": "TT.500"
			}), 500)

		try:
			if args["tts"]:
				result["audio_data"] = tts_func(result["text"])

		except Exception as e:
			logger.error(f"Error during tts process: {e}.\nAborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": GENERAL_ERROR_MESSAGE,
				"error_code": "TT.500"
			}), 500)

		logger.info("Agent response process completed successfully")
		return make_response(jsonify({
			"status": "Success",
			"message": "Agent response process completed successfully",
			"agent_response": result
		}), 201)


api.add_resource(SpeechRecognition, "/asr")
api.add_resource(Agent, "/agent")
