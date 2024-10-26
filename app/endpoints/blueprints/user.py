from typing import Any, Optional
from datetime import timedelta
from logging import Logger, getLogger
from flask_restful import Api, Resource
from werkzeug.exceptions import NotFound
from sqlalchemy.exc import IntegrityError
from flask_restful.reqparse import Namespace
from flask import Blueprint, Response, make_response, jsonify
from flask_jwt_extended import jwt_required, create_access_token

from app.resources.database import db
from app.resources.models import User
from app.resources.functions import encrypt, decrypt
from app.resources.config import PROJECT_NAME, GENERAL_ERROR_MESSAGE
from app.resources.parsers import (
	create_post_user_parser, create_put_user_parser, create_auth_user_parser
)


logger: Logger = getLogger(f"{PROJECT_NAME}.user_blueprint")

user_blueprint: Blueprint = Blueprint("user", __name__)
api: Api = Api(user_blueprint)


class UserList(Resource):
	@jwt_required()
	def get(self) -> Response:
		logger.debug("Getting all users...")
		try:
			users: list = User.query.all()
		except Exception as e:
			logger.error(f"Error getting all users: {e}. Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": GENERAL_ERROR_MESSAGE,
				"error_code": "TT.500"
			}), 500)

		if users is None or users == []:
			logger.info("Request completed successfully but no data found")
			return make_response(jsonify({
				"status": "Success",
				"message": "No data found"
			}), 204)

		logger.debug("Serializing users...")
		result: list[dict] = []
		try:
			for user in users:
				del user.password
				result.append({
					"id": user.id,
					"username": user.username,
					"mail": user.mail,
					"created_at": user.created_at
				})
		except Exception as e:
			logger.error(f"Error serializing users: {e}. Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": GENERAL_ERROR_MESSAGE,
				"error_code": "TT.500"
			}), 500)

		logger.debug("Returning users...")
		return make_response(jsonify({
			"status": "Success",
			"message": "Users queried successfully",
			"users": result
		}), 200)

	def post(self) -> Response:
		logger.debug("Adding new user...")

		logger.debug("Checking request data...")
		args: Namespace = create_post_user_parser()

		logger.debug("Checking if user already exists...")
		try:
			if User.query.filter_by(mail=args["mail"]).first():
				logger.error("User already exists. Aborting request...")
				return make_response(jsonify({
					"status": "Failed",
					"message": "User already exists",
					"error_code": "TT.D409"
				}), 409)

		except Exception as e:
			logger.error(f"Error checking if user already exists: {e}. Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": GENERAL_ERROR_MESSAGE,
				"error_code": "TT.500"
			}), 500)

		logger.debug("Encrypting password...")
		try:
			encripted_password: bytes = encrypt(args["password"])
		except Exception as e:
			logger.error(f"Error encrypting password: {e}. Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": GENERAL_ERROR_MESSAGE,
				"error_code": "TT.500"
			}), 500)

		logger.debug("Creating new user...")
		try:
			new_user: User = User(username=args["username"], mail=args["mail"], password=encripted_password)
			db.session.add(new_user)
			db.session.commit()

		except Exception as e:
			logger.error(f"Error creating new user: {e}. Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": GENERAL_ERROR_MESSAGE,
				"error_code": "TT.500"
			}), 500)

		logger.debug("Returning user id...")
		return make_response(jsonify({
			"status": "Success",
			"message": "User created successfully",
			"id": new_user.id
		}), 201)


class UserDetail(Resource):
	@jwt_required()
	def get(self, id: int) -> Response:
		logger.debug(f"Getting user with id {id}...")
		try:
			user: User = User.query.get_or_404(id)

		except NotFound:
			logger.error("User not found. Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": "User not found",
				"error_code": "TT.D404"
			}), 404)

		except Exception as e:
			logger.error(f"Error getting user: {e}. Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": GENERAL_ERROR_MESSAGE,
				"error_code": "TT.500"
			}), 500)

		logger.debug("Serializing user...")
		try:
			del user.password
			result: dict[str, Any] = {
				"id": user.id,
				"username": user.username,
				"mail": user.mail,
				"created_at": user.created_at
			}

		except Exception as e:
			del user.password
			logger.error(f"Error serializing user: {e}. Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": GENERAL_ERROR_MESSAGE,
				"error_code": "TT.500"
			}), 500)

		logger.debug("Returning user...")
		return make_response(jsonify({
			"status": "Success",
			"message": "User queried successfully",
			"user": result
		}), 200)

	@jwt_required()
	def put(self, id: int) -> Response:
		logger.debug(f"Updating user with id {id}...")

		logger.debug("Checking request data...")
		args: Namespace = create_put_user_parser()

		logger.debug("Checking if user exists...")
		try:
			user: User = User.query.get_or_404(id)

		except NotFound:
			logger.error("User not found. Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": "User not found",
				"error_code": "TT.D404"
			}), 404)

		except Exception as e:
			logger.error(f"Error checking if user exists: {e}. Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": GENERAL_ERROR_MESSAGE,
				"error_code": "TT.500"
			}), 500)

		logger.debug("Updating user...")
		if args["username"]:
			user.username = args["username"]

		if args["mail"]:
			user.mail = args["mail"]

		if args["password"]:
			logger.debug("Encrypting password...")
			try:
				user.password = encrypt(args["password"])

			except Exception as e:
				logger.error(f"Error encrypting password: {e}. Aborting request...")
				return make_response(jsonify({
					"status": "Failed",
					"message": GENERAL_ERROR_MESSAGE,
					"error_code": "TT.500"
				}), 500)

		logger.debug("Committing changes...")
		try:
			db.session.commit()

		except IntegrityError as e:
			logger.error(f"Error committing changes: {e}. Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": "User's mail already exists",
				"error_code": "TT.D409"
			}), 409)

		except Exception as e:
			logger.error(f"Error committing changes: {e}. Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": GENERAL_ERROR_MESSAGE,
				"error_code": "TT.500"
			}), 500)

		logger.debug("Returning user id...")
		return make_response(jsonify({
			"status": "Success",
			"message": "User updated successfully",
			"id": id
		}), 201)

	@jwt_required()
	def delete(self, id: int) -> Response:
		logger.debug(f"Deleting user with id {id}...")

		logger.debug("Checking if user exists...")
		try:
			user: User = User.query.get_or_404(id)

		except NotFound:
			logger.error("User not found. Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": "User not found",
				"error_code": "TT.D404"
			}), 404)

		except Exception as e:
			logger.error(f"Error checking if user exists: {e}. Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": GENERAL_ERROR_MESSAGE,
				"error_code": "TT.500"
			}), 500)

		logger.debug("Deleting user...")
		try:
			db.session.delete(user)
			db.session.commit()

		except Exception as e:
			logger.error(f"Error deleting user: {e}. Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": GENERAL_ERROR_MESSAGE,
				"error_code": "TT.500"
			}), 500)

		logger.debug("Returning success message...")
		return make_response(jsonify({
			"status": "Success",
			"message": "User deleted successfully",
		}), 200)


class UserAuth(Resource):
	def post(self) -> Response:
		logger.debug("Authenticating user...")

		logger.debug("Checking request data...")
		args: Namespace = create_auth_user_parser()

		logger.debug("Checking if user exists...")
		try:
			user: Optional[User] = User.query.filter_by(mail=args["mail"]).first()

		except Exception as e:
			logger.error(f"Error checking if user exists: {e}. Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": GENERAL_ERROR_MESSAGE,
				"error_code": "TT.500"
			}), 500)

		if user is None or user == []:
			logger.error("User not found. Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": "User not found",
				"error_code": "TT.D404"
			}), 404)

		logger.debug("Authenticating user...")
		try:
			password: str = decrypt(user.password)
			del user.password

		except Exception as e:
			logger.error(f"Error decrypting password: {e}. Aborting request...")
			del user.password
			return make_response(jsonify({
				"status": "Failed",
				"message": GENERAL_ERROR_MESSAGE,
				"error_code": "TT.500"
			}), 500)

		if args["password"] != password:
			logger.error("Invalid password. Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": "Invalid password",
				"error_code": "TT.D401"
			}), 401)

		logger.debug("Generating new JWT...")
		expires: timedelta = timedelta(days=1)
		access_token: str = create_access_token(
			{
				"id": user.id,
				"username": user.username,
				"mail": user.mail,
				"created_at": user.created_at
			},
			expires_delta=expires
		)

		logger.debug("Returning success message...")
		return make_response(jsonify({
			"status": "Success",
			"message": "User authenticated successfully",
			"id": user.id,
			"token": access_token,
			"username": user.username,
			"created_at": user.created_at
		}), 201)


api.add_resource(UserList, '/')
api.add_resource(UserAuth, "/auth")
api.add_resource(UserDetail, "/<int:id>")
