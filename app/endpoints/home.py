from flask_restful import Resource
from flask import Response, make_response, jsonify


class Home(Resource):
	def get(self) -> Response:
		return make_response(jsonify({
			"status": "Success",
			"message": (
				"Welcome to Tip Trip. Hope this tool helps you to improve your "
				"travel experiences"
			)
		}), 200)
