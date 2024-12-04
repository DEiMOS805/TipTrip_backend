from datetime import timedelta
from typing import Any, Optional
from logging import Logger, getLogger
from flask_restful import Api, Resource
from werkzeug.exceptions import NotFound
from sqlalchemy.exc import IntegrityError
from flask_restful.reqparse import Namespace
from flask import Blueprint, Response, make_response, jsonify
from flask_jwt_extended import jwt_required, get_jwt, create_access_token

from app.resources.parsers import *
from app.resources.database import db
from app.resources.models import User, Favorite, Place
from app.resources.config import PROJECT_NAME, GENERAL_ERROR_MESSAGE
from app.resources.functions import encrypt, decrypt, get_place_distance


logger: Logger = getLogger(f"{PROJECT_NAME}.user_blueprint")

user_blueprint: Blueprint = Blueprint("user", __name__)
api: Api = Api(user_blueprint)


class UserList(Resource):
	@jwt_required()
	def get(self) -> Response:
		logger.debug("Getting all users...")

		logger.info("Checking user permissions...")
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
			"message": "Users retrieved successfully",
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
			db.session.rollback()

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
	def post(self, id: int) -> Response:
		logger.debug(f"Adding coordinates for user with id {id}...")

		logger.debug("Checking request data...")
		args: Namespace = create_post_coordinates_parser()

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

		logger.debug("Updating user's coordinates...")
		try:
			user.latitude = args["latitude"]
			user.longitude = args["longitude"]
			db.session.commit()

		except Exception as e:
			logger.error(f"Error updating user's coordinates: {e}. Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": GENERAL_ERROR_MESSAGE,
				"error_code": "TT.500"
			}), 500)

		logger.debug("Returning user id...")
		return make_response(jsonify({
			"status": "Success",
			"message": "User's coordinates updated successfully",
			"id": id
		}), 201)

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
			db.session.rollback()

			return make_response(jsonify({
				"status": "Failed",
				"message": "User's mail already exists",
				"error_code": "TT.D409"
			}), 409)

		except Exception as e:
			logger.error(f"Error committing changes: {e}. Aborting request...")
			db.session.rollback()

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
			db.session.rollback()

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

		try:
			logger.debug("Generating new JWT...")
			expires: timedelta = timedelta(days=1)
			access_token: str = create_access_token(
				{
					"id": user.id,
					"username": user.username,
					"mail": user.mail,
					"is_admin": user.is_admin,
					"created_at": user.created_at
				},
				expires_delta=expires
			)

		except Exception as e:
			logger.error(f"Error generating new JWT: {e}. Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": GENERAL_ERROR_MESSAGE,
				"error_code": "TT.500"
			}), 500)

		logger.debug("Returning success message...")
		return make_response(jsonify({
			"status": "Success",
			"message": "User authenticated successfully",
			"id": user.id,
			"token": access_token,
			"username": user.username,
			"created_at": user.created_at
		}), 201)


class UserVerify(Resource):
	def post(self) -> Response:
		logger.debug("Verifying user existence...")

		logger.debug("Checking request data...")
		args: Namespace = create_verify_user_parser()

		logger.debug("Checking if user exists...")
		try:
			user: User = User.query.filter_by(mail=args["mail"]).first()

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

		try:
			logger.debug("Generating new JWT...")
			expires: timedelta = timedelta(days=1)
			access_token: str = create_access_token(
				{
					"id": user.id,
					"username": user.username,
					"mail": user.mail,
					"is_admin": user.is_admin,
					"created_at": user.created_at
				},
				expires_delta=expires
			)

		except Exception as e:
			logger.error(f"Error generating new JWT: {e}. Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": GENERAL_ERROR_MESSAGE,
				"error_code": "TT.500"
			}), 500)

		logger.debug("Returning success message...")
		return make_response(jsonify({
			"status": "Success",
			"message": "User verified successfully",
			"id": user.id,
			"token": access_token
		}), 201)


class UserFavoriteList(Resource):
	@jwt_required()
	def get(self) -> Response:
		logger.debug("Getting all users favorites places...")

		logger.info("Checking user permissions...")
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
			favorites: list = Favorite.query.all()

		except Exception as e:
			logger.error(f"Error getting all favorites: {e}. Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": GENERAL_ERROR_MESSAGE,
				"error_code": "TT.500"
			}), 500)

		if favorites is None or favorites == []:
			logger.info("Request completed successfully but no data found")
			return make_response(jsonify({
				"status": "Success",
				"message": "No data found"
			}), 204)

		logger.debug("Serializing favorites...")
		result: dict = {}
		try:
			for favorite in favorites:
				user_id: int = favorite.user.id

				if user_id not in result:
					result[user_id] = {
						"user": {
							"id": user_id,
							"username": favorite.user.username,
							"mail": favorite.user.mail,
						},
						"favorites": []
					}

				result[user_id]["favorites"].append({
					"id": favorite.place.id,
					"name": favorite.place.name,
					"classification": favorite.place.classification,
					"punctuation": favorite.place.punctuation,
					"created_at": favorite.created_at
				})

			result: list = list(result.values())

		except Exception as e:
			logger.error(f"Error serializing favorites: {e}. Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": GENERAL_ERROR_MESSAGE,
				"error_code": "TT.500"
			}), 500)

		logger.debug("Returning favorites...")
		return make_response(jsonify({
			"status": "Success",
			"message": "All favorites places retrieved successfully",
			"favorites": result
		}), 200)

	@jwt_required()
	def post(self) -> Response:
		logger.debug("Adding user's new favorite place...")

		logger.debug("Checking request data...")
		args: Namespace = create_post_favorite_parser()

		logger.debug("Checking if user and place exist...")
		try:
			user: Optional[Any] = User.query.get(args["user_id"])
			place: Optional[Any] = Place.query.get(args["place_id"])

			if not user:
				logger.error("User not found. Aborting request...")
				return make_response(jsonify({
					"status": "Failed",
					"message": "User not found",
					"error_code": "TT.D404"
				}), 404)

			if not place:
				logger.error("Place not found. Aborting request...")
				return make_response(jsonify({
					"status": "Failed",
					"message": "Place not found",
					"error_code": "TT.D404"
				}), 404)

		except Exception as e:
			logger.error(f"Error checking user/place existence: {e}. Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": "An error occurred while checking user/place existence",
				"error_code": "TT.500"
			}), 500)

		logger.debug("Checking if favorite already exists...")
		try:
			existing_favorite = Favorite.query.filter_by(id_user=args["user_id"], id_place=args["place_id"]).first()
			if existing_favorite:
				logger.error(f"Favorite place with id {args['place_id']} already exists for user with id {args['user_id']}. Aborting request...")
				return make_response(jsonify({
					"status": "Failed",
					"message": f"Favorite place with id {args['place_id']} already exists for user with id {args['user_id']}",
					"error_code": "TT.D409"
				}), 409)

		except Exception as e:
			logger.error(f"Error checking if favorite place exists: {e}. Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": "An error occurred while checking favorite place existence.",
				"error_code": "TT.500"
			}), 500)

		# Crear nuevo favorito
		logger.debug("Creating new favorite place...")
		try:
			new_favorite = Favorite(id_user=args["user_id"], id_place=args["place_id"])
			db.session.add(new_favorite)
			db.session.commit()

		except Exception as e:
			logger.error(f"Error creating new favorite place: {e}. Aborting request...")
			db.session.rollback()

			return make_response(jsonify({
				"status": "Failed",
				"message": "An error occurred while creating the favorite place.",
				"error_code": "TT.500"
			}), 500)

		logger.debug("Favorite place created successfully")
		return make_response(jsonify({
			"status": "Success",
			"message": "Favorite place created successfully for given user",
			"favorite": {
				"user_id": new_favorite.id_user,
				"place_id": new_favorite.id_place
			}
		}), 201)


class UserFavoriteDetail(Resource):
	@jwt_required()
	def get(self, id: int) -> Response:
		logger.debug(f"Getting all favorite places for user with id {id}...")

		logger.debug("Checking request data for user coordinates...")
		args: Namespace = create_get_favorite_parser()

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

		logger.debug("Getting user's favorite places...")
		try:
			favorites: list = Favorite.query.filter_by(id_user=id).all()

		except Exception as e:
			logger.error(f"Error getting user's favorite places: {e}. Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": GENERAL_ERROR_MESSAGE,
				"error_code": "TT.500"
			}), 500)

		if favorites is None or favorites == []:
			logger.info("Request completed successfully but no data found")
			return make_response(jsonify({
				"status": "Success",
				"message": "No data found"
			}), 204)

		logger.debug("Serializing favorite places...")
		result: list = []
		try:
			for favorite in favorites:
				result.append({
					"id": favorite.place.id,
					"name": favorite.place.name,
					"classification": favorite.place.classification,
					"address": (
						f"{favorite.place.address.street_number}, "
						f"{favorite.place.address.colony}, "
						f"{favorite.place.address.cp}, "
						f"{favorite.place.address.municipality}, "
						f"{favorite.place.address.state}."
					),
					"punctuation": favorite.place.punctuation,
					"created_at": favorite.created_at,
					"latitude": favorite.place.address.latitude,
					"longitude": favorite.place.address.longitude
				})

		except Exception as e:
			logger.error(f"Error serializing favorite places: {e}. Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": GENERAL_ERROR_MESSAGE,
				"error_code": "TT.500"
			}), 500)

		if args["current_latitude"] is not None and args["current_longitude"] is not None:
			try:
				logger.debug("Calculating places distances...")
				for place in result:
					place["distance"] = get_place_distance(
						(args["current_latitude"], args["current_longitude"]),
						(place["latitude"], place["longitude"])
					)
					del place["latitude"]
					del place["longitude"]

				logger.debug("Sorting places by distance...")
				result.sort(key=lambda place: place["distance"])

			except Exception as e:
				logger.error(f"Error calculating places distance: {e}. Aborting request...")
				return make_response(jsonify({
					"status": "Failed",
					"message": GENERAL_ERROR_MESSAGE,
					"error_code": "TT.500"
				}), 500)

		else:
			logger.debug("No current user coordinates provided...")
			for place in result:
				place["distance"] = None

		logger.debug("Returning favorite places...")
		return make_response(jsonify({
			"status": "Success",
			"message": "Favorite places retrieved successfully for given user",
			"user_id": id,
			"favorites": result
		}), 200)


class UserFavoriteDelete(Resource):
	@jwt_required()
	def delete(self, id_user: int, id_place: int) -> Response:
		logger.debug(f"Removing user's id {id_user} favorite place with id {id_place}...")

		logger.debug("Checking if user's favorite place exists...")
		try:
			favorite: Favorite = Favorite.query.filter_by(id_user=id_user, id_place=id_place).first()

			if not favorite or favorite == []:
				logger.error("User's favorite place not found. Aborting request...")
				return make_response(jsonify({
					"status": "Failed",
					"message": "User's favorite not found",
					"error_code": "TT.D404"
				}), 404)

		except Exception as e:
			logger.error(f"Error checking if user's favorite place exists: {e}. Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": GENERAL_ERROR_MESSAGE,
				"error_code": "TT.500"
			}), 500)

		logger.debug("Deleting user's favorite place...")
		try:
			db.session.delete(favorite)
			db.session.commit()

		except Exception as e:
			logger.error(f"Error deleting user's favorite place: {e}. Aborting request...")
			db.session.rollback()

			return make_response(jsonify({
				"status": "Failed",
				"message": GENERAL_ERROR_MESSAGE,
				"error_code": "TT.500"
			}), 500)

		logger.debug("Returning success message...")
		return make_response(jsonify({
			"status": "Success",
			"message": "User's favorite place deleted successfully",
		}), 200)


api.add_resource(UserList, '/')
api.add_resource(UserAuth, "/auth")
api.add_resource(UserVerify, "/verify")
api.add_resource(UserDetail, "/<int:id>")
api.add_resource(UserFavoriteList, "/favorites")
api.add_resource(UserFavoriteDetail, "/favorites/<int:id>")
api.add_resource(UserFavoriteDelete, "/favorites/<int:id_user>/<int:id_place>")
