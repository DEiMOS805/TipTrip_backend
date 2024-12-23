from flask_restful import Resource
from logging import Logger, getLogger
from flask import Response, send_from_directory, make_response, jsonify

from app.resources.config import PROJECT_NAME, GENERAL_ERROR_MESSAGE, STATIC_ABSPATH


logger: Logger = getLogger(f"{PROJECT_NAME}.download_endpoint")


class Download(Resource):
	def get(self, os: str) -> Response:
		if os not in ["android", "ios"]:
			logger.error("OS not found. Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": "OS not found",
				"error_code": "TT.D404"
			}), 404)

		logger.debug(f"Downloading instaler file with tag {os}...")
		try:
			if os == "android":
				filename: str = "tiptrip.apk"
			else:
				filename: str = "tiptrip.ipa"

			logger.info(f"Sending installer file {filename} to the client...")
			return send_from_directory(STATIC_ABSPATH, filename, as_attachment=True)

		except Exception as e:
			logger.error(f"Error while downloading installer file: {e}")
			return make_response(jsonify({
				"status": "Failed",
				"message": GENERAL_ERROR_MESSAGE,
				"error_code": "TT.D500"
			}), 500)
