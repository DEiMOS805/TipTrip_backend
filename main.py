from flask.wrappers import Response
from flask import make_response, jsonify
from flask_jwt_extended import jwt_required

from app import app, api
from app.endpoints.auth import Auth
from app.endpoints.get_record import GetRecord
from app.endpoints.get_demo_data import GetDemoData


api.add_resource(Auth, "/auth")
api.add_resource(GetRecord, "/get_record")
api.add_resource(GetDemoData, "/get_demo_data")


@app.route('/')
@jwt_required()
def home() -> dict:
	""" Home route """
	response: dict = {
		"status": "Correct",
		"message": "Bienvenido a Tip Trip. Esperamos te ayude a mejorar tus viajes"
	}
	return make_response(jsonify(response), 200)


@app.after_request
def appy_caching(response: Response) -> Response:
	""" Apply caching to all responses """
	app.logger.info(app.logger)
	return response


if __name__ == "__main__":
	app.run(host="0.0.0.0", port=5000, debug=True)
