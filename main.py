from flask.wrappers import Response
from flask import make_response, jsonify
from flask_jwt_extended import jwt_required

from app import app, api
from app.endpoints.users.auth import Auth
from app.endpoints.users.add_user import AddUser
from app.endpoints.data.get_record import GetRecord
from app.endpoints.data.get_demo_data import GetDemoData
from app.endpoints.models.speech_recognition import SpeechRecognition


api.add_resource(Auth, "/auth_user")
api.add_resource(AddUser, "/add_user")
api.add_resource(GetRecord, "/get_record")
api.add_resource(GetDemoData, "/get_demo_data")
api.add_resource(SpeechRecognition, "/speech_recognition")


@app.route('/')
@jwt_required()
def home() -> dict:
	""" Home route """
	response: dict = {
		"status": "Success",
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
