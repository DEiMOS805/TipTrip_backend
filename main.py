from flask.wrappers import Response
from flask import make_response, jsonify

from app import app, api, auth
from app.endpoints.get_record import GetRecord
from app.endpoints.get_all_records import GetAllRecords


api.add_resource(GetRecord, "/get_record")
api.add_resource(GetAllRecords, "/get_all_records")


@app.route('/')
@auth.login_required
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
