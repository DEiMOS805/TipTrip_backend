"""
File to handle APIs errors

Errors codes glossary:

Bad request (00400)
00401 => Missing request data
00402 => Incorrect request data type
00404 => Resource (link) not found

Other errors (00500)
00501 => Internal server error
"""

from logging import getLogger
from flask import make_response, jsonify
from werkzeug.exceptions import HTTPException

from app import app
from app.resources.config import PROJECT_NAME, GENERAL_ERROR_MESSAGE


logger = getLogger(f"{PROJECT_NAME}.error_manager")


# def get_error_code(message: str) -> int:
#     """ Function to return a internal API error code based on a given message """
#     if message == "":
#         return 400
#     elif message == "":
#         return 401


def make_error_response(message: str, http_code: int) -> dict:
    """ Function to return each error with the same format """
    response: dict = {
        "status": "Failed",
        "error_message": message
    }
    return make_response(jsonify(response), http_code)


@app.errorhandler(KeyError)
def key_error_handler(error: KeyError) -> dict:
    """ Function to handle KeyError errors """
    error = str(error)

    if not any(
        f"'{key}'" == error for key in
        ["table_name", "place_name", "email", "password"]
    ):
        logger.error(error)
        return make_error_response(GENERAL_ERROR_MESSAGE, http_code=500)
    else:
        return make_error_response(
            message=f"Missing request data field: {error}",
            http_code=400
        )


@app.errorhandler(TypeError)
def type_error_handler(error: TypeError) -> dict:
    """ Function to handle TypeError errors """
    error = str(error)

    if not any(
        f"'{key}'" == error for key in
        ["table_name", "place_name", "email", "password"]
    ):
        logger.error(error)
        return make_error_response(GENERAL_ERROR_MESSAGE, http_code=500)
    else:
        return make_error_response(
            message=f"Data field ({error}) has the wrong data type (str)",
            http_code=400
        )

@app.errorhandler(HTTPException)
def not_found_error_handler(error: HTTPException) -> dict:
    """ Function that handles the error 404 """
    return make_error_response("00404", str(error), 404)

@app.errorhandler(Exception)
def exception_error_handler(error: Exception) -> dict:
    """ Function that handles general Exception errors """
    return make_error_response("00500", GENERAL_ERROR_MESSAGE, 500)


# @app.errorhandler(KeyError)
# def key_error_handler(error):
#     print(str(error))
#     """
#     Function to handle errors when the request data fields are missing
#     or other KeyError cases
#     """
#     # Case when request data field "file_category" is missing
#     if "file_category" in str(error):
#         return make_error_response(
#             "00201",
#             "Missing request data field: file_category",
#             400)
#     # Case when request data field "file_data" is missing
#     elif "file_data" in str(error):
#         return make_error_response(
#             "00201",
#             "Missing request data field: file_data",
#             400)
#     # Case when no authorization token is provided
#     elif "HTTP_AUTHORIZATION" in str(error):
#         return make_error_response(
#             "00101",
#             "Missing authorization token",
#             400)
#     else:
#         return make_error_response("00501", str(error), 500)


# @app.errorhandler(TypeError)
# def type_error_handler(error):
#     """
#     Function to handle errors when the request data fields are not of string
#     data type or other TypeError cases
#     """
#     if "file_category" in str(error) or "file_data" in str(error):
#         return make_error_response(
#             "00202",
#             "Request data fields must be of string type",
#             400)
#     return make_error_response("00501", str(error), 500)


# @app.errorhandler(ValueError)
# def value_error_handler(error):
#     """ Function to return the errors caused by the ValueError error """
#     if "tipo de documento" in str(error):
#         return make_error_response(
#             "00203",
#             "Request file category not allowed to be processed",
#             400)
#     return make_error_response("00501", str(error), 500)


# @app.errorhandler(IOError)
# @app.errorhandler(IndexError)
# @app.errorhandler(PdfiumError)
# @app.errorhandler(MemoryError)
# @app.errorhandler(binascii.Error)
# @app.errorhandler(AttributeError)
# @app.errorhandler(UnicodeDecodeError)
# def general_error_handler(error):
#     """ Function to return the errors caused by different exceptions """
#     return make_error_response("00501", str(error), 500)
