"""
File to handle APIs errors

Errors codes glossary:

Bad request (00400)
TT.D400 => Missing request data
TT.D401 => Incorrect request data type
TT.D402 => Bad username or password
TT.D409 => Email already exists in db
TT.D410 => Bad audio file

TT.R404 => Resource (link) not found

Other errors (00500)
TT.E500 => Internal server error
"""

from logging import getLogger
from flask import make_response, jsonify
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import HTTPException

from app import app
from app.resources.config import PROJECT_NAME, GENERAL_ERROR_MESSAGE


logger = getLogger(f"{PROJECT_NAME}.error_manager")


def make_error_response(message: str, error_code: str, http_code: int) -> dict:
	""" Function to return each error with the same format """
	response: dict = {
		"status": "Failed",
		"message": message,
		"error_code": error_code
	}
	return make_response(jsonify(response), http_code)


@app.errorhandler(KeyError)
def key_error_handler(error: KeyError) -> dict:
	""" Function to handle KeyError errors """
	error = str(error)

	if error == "'TT.D402'":
		return make_error_response(
			message="Bad username or password",
			error_code="TT.D402",
			http_code=401
		)
	elif not any(
		f"'{key}'" == error for key in
		["place_name", "email", "password", "audio_data"]
	):
		logger.error(error)
		return make_error_response(
			message=GENERAL_ERROR_MESSAGE,
			error_code="TT.E500",
			http_code=500
		)
	else:
		return make_error_response(
			message=f"Missing request data field: {error}",
			error_code="TT.D401",
			http_code=400
		)


@app.errorhandler(TypeError)
def type_error_handler(error: TypeError) -> dict:
	""" Function to handle TypeError errors """
	error = str(error)

	if not any(
		f"'{key}'" == error for key in
		["place_name", "email", "password", "category", "municipality", "audio_data"]
	):
		logger.error(error)
		return make_error_response(
			message=GENERAL_ERROR_MESSAGE,
			error_code="TT.E500",
			http_code=500
		)
	else:
		return make_error_response(
			message=f"Data field ({error}) has the wrong data type (str)",
			error_code="TT.D401",
			http_code=400
		)


@app.errorhandler(ValueError)
def value_error_handler(error: ValueError) -> dict:
	""" Function to handle ValueError errors """
	if str(error) == "vosk_audio_file":
		return make_error_response(
			message=(
				"El archivo de audio debe estar en formato mono, "
				"16-bit y con una tasa de muestreo de 16000 o 8000 Hz"
			),
			error_code="TT.D410",
			http_code=410
		)
	else:
		logger.error(error)
		return make_error_response(
			message=GENERAL_ERROR_MESSAGE,
			error_code="TT.E500",
			http_code=500
		)


@app.errorhandler(HTTPException)
def not_found_error_handler(error: HTTPException) -> dict:
	""" Function that handles the error 404 """
	return make_error_response(str(error), "TT.R404", 404)


@app.errorhandler(IntegrityError)
def not_found_error_handler(error: IntegrityError) -> dict:
	""" Function that handles the error IntegrityError """
	return make_error_response(
		message="Email already exists in db",
		error_code="TT.D409",
		http_code=409
	)


@app.errorhandler(Exception)
def exception_error_handler(error: Exception) -> dict:
	""" Function that handles general Exception errors """
	return make_error_response(GENERAL_ERROR_MESSAGE, "TT.E500", 500)
