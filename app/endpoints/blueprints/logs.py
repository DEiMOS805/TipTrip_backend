from os.path import join
from pytz import timezone
from base64 import b64decode
from datetime import datetime
from os import listdir, remove
from logging import Logger, getLogger
from flask_restful import Api, Resource
from flask_restful.reqparse import Namespace
from flask_jwt_extended import jwt_required, get_jwt
from flask import Blueprint, Response, make_response, jsonify, send_from_directory

from app.resources.config import *
from app.resources.parsers import *


logger: Logger = getLogger(f"{PROJECT_NAME}.log_blueprint")

log_blueprint: Blueprint = Blueprint("log", __name__)
api: Api = Api(log_blueprint)


class LogList(Resource):
	@jwt_required()
	def get(self) -> Response:
		logger.debug("Getting all .log file names saved...")

		logger.debug("Checking user permissions...")
		jwt_data: dict = get_jwt()
		is_admin: bool = jwt_data["sub"]["is_admin"]
		if not is_admin:
			logger.error("Forbidden access for given user. Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": "Forbidden access",
				"error_code": "TT.D403"
			}), 403)

		try:
			temp_dir_content: list[str] = listdir(TEMP_ABSPATH)
			log_files: list[str] = [file for file in temp_dir_content if file.endswith(".log")]
		except Exception as e:
			logger.error(f"An error ocurred while getting .log files: {e}")
			return make_response(jsonify({
				"status": "Failed",
				"message": GENERAL_ERROR_MESSAGE,
				"error_code": "TT.D500"
			}), 500)

		if log_files is None or log_files == []:
			logger.info("Request completed successfully but no data found...")
			return make_response(jsonify({
				"status": "Success",
				"message": "No data found",
			}), 204)

		logger.info("Returning log filenames...")
		return make_response(jsonify({
			"status": "Success",
			"message": "Log filenames retrieved successfully",
			"log_files": log_files
		}), 200)

	def post(self) -> Response:
		logger.debug("Creating a new .log file...")

		logger.debug("Checking request data...")
		args: Namespace = create_post_log_parser()

		logger.debug("Decoding given file data...")
		try:
			file_data: bytes = b64decode(args["file"])
		except Exception as e:
			logger.error(f"Error decoding file data: {e}. Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": GENERAL_ERROR_MESSAGE,
				"error_code": "TT.D500"
			}), 500)

		logger.debug("Saving file data as a .log file...")
		try:
			filename: str = f"{args['user_id']}_{datetime.now(timezone('America/Mexico_City')).strftime('%Y_%m_%d_%H_%M_%S')}.log"
			with open(join(TEMP_ABSPATH, filename), "wb") as file:
				file.write(file_data)

		except Exception as e:
			logger.error(f"Error saving file data: {e}. Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": GENERAL_ERROR_MESSAGE,
				"error_code": "TT.D500"
			}), 500)

		logger.info("File saved successfully...")
		return make_response(jsonify({
			"status": "Success",
			"message": "File saved successfully",
			"filename": filename
		}), 201)


class LogDetail(Resource):
	@jwt_required()
	def get(self, filename: str) -> Response:
		logger.debug(f"Getting {filename}.log...")

		logger.debug("Checking user permissions...")
		jwt_data: dict = get_jwt()
		is_admin: bool = jwt_data["sub"]["is_admin"]
		if not is_admin:
			logger.error("Forbidden access for given user. Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": "Forbidden access",
				"error_code": "TT.D403"
			}), 403)

		logger.debug("Checking if file exists...")
		try:
			temp_dir_content: list[str] = listdir(TEMP_ABSPATH)
			exists: bool = filename in temp_dir_content
		except Exception as e:
			logger.error(f"Error reading file: {e}. Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": GENERAL_ERROR_MESSAGE,
				"error_code": "TT.D500"
			}), 500)

		if not exists:
			logger.error("File not found. Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": "File not found",
				"error_code": "TT.D404"
			}), 404)

		logger.info("Returning file data...")
		return send_from_directory(TEMP_ABSPATH, filename, as_attachment=True)

	@jwt_required()
	def delete(self, filename: str) -> Response:
		logger.debug(f"Deleting {filename}.log...")

		logger.debug("Checking user permissions...")
		jwt_data: dict = get_jwt()
		is_admin: bool = jwt_data["sub"]["is_admin"]
		if not is_admin:
			logger.error("Forbidden access for given user. Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": "Forbidden access",
				"error_code": "TT.D403"
			}), 403)

		logger.debug("Checking if file exists...")
		try:
			temp_dir_content: list[str] = listdir(TEMP_ABSPATH)
			exists: bool = filename in temp_dir_content
		except Exception as e:
			logger.error(f"Error reading file: {e}. Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": GENERAL_ERROR_MESSAGE,
				"error_code": "TT.D500"
			}), 500)

		if not exists:
			logger.error("File not found. Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": "File not found",
				"error_code": "TT.D404"
			}), 404)

		logger.debug("Deleting file...")
		try:
			remove(join(TEMP_ABSPATH, filename))
		except Exception as e:
			logger.error(f"Error deleting file: {e}. Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": GENERAL_ERROR_MESSAGE,
				"error_code": "TT.D500"
			}), 500)

		logger.info("File deleted successfully...")
		return make_response(jsonify({
			"status": "Success",
			"message": "File deleted successfully"
		}), 200)


api.add_resource(LogList, '/')
api.add_resource(LogDetail, "/<string:filename>")
