# from flask_jwt_extended import JWTManager
# from werkzeug.exceptions import HTTPException
# from flask import Flask, Response, make_response, jsonify
# from jwt import ExpiredSignatureError, InvalidSignatureError
# from flask_jwt_extended.exceptions import NoAuthorizationError, InvalidHeaderError, RevokedTokenError, UserLookupError


# def set_error_handlers(app: Flask, jwt: JWTManager) -> None:
# 	@jwt.unauthorized_loader
# 	def handle_unauthorized_token(e) -> Response:
# 		return make_response(jsonify({
# 			"status": "Failed",
# 			"message": "Unauthorized token",
# 			"error_code": "TT.401"
# 		}), 401)

# 	@app.errorhandler(HTTPException)
# 	def not_found_error_handler(error: HTTPException) -> Response:
# 		""" Function that handles the error 404 """
# 		return make_response(jsonify({
# 			"status": "Failed",
# 			"message": "Resource not found",
# 			"error_code": "TT.404"
# 		}), 404)

# 	@app.errorhandler(ExpiredSignatureError)
# 	def handle_expired_token(error: ExpiredSignatureError) -> Response:
# 		return make_response(jsonify({
# 			"status": "Failed",
# 			"message": "Token already expired",
# 			"error_code": "TT.401"
# 		}), 401)

# 	@app.errorhandler(InvalidSignatureError)
# 	def handle_invalid_signature(error: InvalidSignatureError) -> Response:
# 		return make_response(jsonify({
# 			"status": "Failed",
# 			"message": "Invalid token signature",
# 			"error_code": "TT.401"
# 		}), 401)

# 	@app.errorhandler(InvalidHeaderError)
# 	def handle_invalid_token(error: InvalidHeaderError) -> Response:
# 		return make_response(jsonify({
# 			"status": "Failed",
# 			"message": "Invalid token",
# 			"error_code": "TT.401"
# 		}), 401)

# 	@app.errorhandler(NoAuthorizationError)
# 	def handle_missing_token(error: NoAuthorizationError) -> Response:
# 		return make_response(jsonify({
# 			"status": "Failed",
# 			"message": "Missing token",
# 			"error_code": "TT.401"
# 		}), 401)

# 	@app.errorhandler(RevokedTokenError)
# 	def handle_revoked_token(error: RevokedTokenError) -> Response:
# 		return make_response(jsonify({
# 			"status": "Failed",
# 			"message": "Token revoked",
# 			"error_code": "TT.401"
# 		}), 401)

# 	@app.errorhandler(UserLookupError)
# 	def handle_user_lookup_error(error: UserLookupError) -> Response:
# 		return make_response(jsonify({
# 			"status": "Failed",
# 			"message": "User not found",
# 			"error_code": "TT.404"
# 		}), 404)
