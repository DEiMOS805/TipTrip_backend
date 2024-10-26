from typing import Any
from logging import Logger, getLogger
from sqlalchemy.orm.query import Query
from flask_restful import Api, Resource
from werkzeug.exceptions import NotFound
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import jwt_required
from flask_restful.reqparse import Namespace
from flask import Blueprint, Response, make_response, jsonify

from app.resources.database import db
from app.resources.functions import get_place_distance
from app.resources.models import Place, Review, Address
from app.resources.config import PROJECT_NAME, GENERAL_ERROR_MESSAGE
from app.resources.parsers import (
	create_post_place_parser, create_put_place_parser, create_get_place_parser
)


logger: Logger = getLogger(f"{PROJECT_NAME}.place_blueprint")

place_blueprint: Blueprint = Blueprint("place", __name__)
api: Api = Api(place_blueprint)


class PlaceList(Resource):
	@jwt_required()
	def get(self) -> Response:
		logger.debug("Getting all places...")

		logger.debug("Checking request data...")
		args: Namespace = create_get_place_parser()

		try:
			filters: list = []
			if args["classification"]:
				filters.append(Place.classification == args["classification"])
			if args["municipality"]:
				filters.append(Address.municipality == args["municipality"])

			query: Query[Place] = db.session.query(Place) \
				.outerjoin(Address, Address.id_place == Place.id) \
				.outerjoin(Review, Review.id_place == Place.id)

			if filters != []:
				query = query.filter(*filters)

			places: list[Place] = query.all()

		except Exception as e:
			logger.error(f"Error getting all places: {e}. Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": GENERAL_ERROR_MESSAGE,
				"error_code": "TT.500"
			}), 500)

		if places is None or places == []:
			logger.info("Request completed successfully but no data found")
			return make_response(jsonify({
				"status": "Success",
				"message": "No data found"
			}), 204)

		logger.debug("Serializing places...")
		result: list[dict] = []
		try:
			for place in places:
				result.append({
					"id": place.id,
					"info": {
						"name": place.name,
						"classification": place.classification,
						"punctuation": place.punctuation,
						"description": place.description,
						"schedules": place.schedules,
						"services": place.services,
						"activities": place.activities,
						"prices": place.prices,
						"permanent_exhibitions": place.permanent_exhibitions,
						"temporal_exhibitions": place.temporal_exhibitions,
						"mail": place.mail,
						"phone": place.phone,
						"website": place.website,
						"sic_website": place.sic_website,
					},
					"address": {
						"street_number": place.address.street_number,
						"colony": place.address.colony,
						"municipality": place.address.municipality,
						"state": place.address.state,
						"cp": place.address.cp,
						"latitude": place.address.latitude,
						"longitude": place.address.longitude,
						"how_to_arrive": place.address.how_to_arrive
					},
					"reviews": {
						"general": place.reviews.review,
						"historic": place.reviews.historic_review
					},
					"created_at": place.created_at
				})

		except Exception as e:
			logger.error(f"Error serializing places: {e}. Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": GENERAL_ERROR_MESSAGE,
				"error_code": "TT.500"
			}), 500)

		if args["distance"] and args["current_latitude"] and args["current_longitude"]:
			logger.debug("Calculating places distances...")

			try:
				for place in result:
					place["distance"] = get_place_distance(
						(args["current_latitude"], args["current_longitude"]),
						(place["address"]["latitude"], place["address"]["longitude"])
					)

			except Exception as e:
				logger.error(f"Error calculating places distance: {e}. Aborting request...")
				return make_response(jsonify({
					"status": "Failed",
					"message": GENERAL_ERROR_MESSAGE,
					"error_code": "TT.500"
				}), 500)

			logger.debug("Filtering places by distance...")
			result = [place for place in result if place["distance"] <= args["distance"]]

			logger.debug("Sorting places by distance...")
			result.sort(key=lambda place: place["distance"])

		logger.debug("Returning places...")
		return make_response(jsonify({
			"status": "Success",
			"message": "Places retrieved successfully",
			"places": result
		}), 200)

	@jwt_required()
	def post(self) -> Response:
		logger.debug("Adding new place...")

		logger.debug("Checking request data...")
		args: Namespace = create_post_place_parser()

		logger.debug("Checking if place already exists...")
		try:
			if Place.query.filter_by(name=args["name"]).first():
				logger.error("Place already exists. Aborting request...")
				return make_response(jsonify({
					"status": "Failed",
					"message": "Place already exists",
					"error_code": "TT.D409"
				}), 409)

		except Exception as e:
			logger.error(f"Error checking if place already exists: {e}. Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": GENERAL_ERROR_MESSAGE,
				"error_code": "TT.500"
			}), 500)

		logger.debug("Creating new place...")
		try:
			new_place: Place = Place(
				name=args["name"],
				classification=args["classification"],
				punctuation=args["punctuation"],
				description=args["description"],
				schedules=args["schedules"],
				services=args["services"],
				activities=args["activities"],
				prices=args["prices"],
				permanent_exhibitions=args["permanent_exhibitions"],
				temporal_exhibitions=args["temporal_exhibitions"],
				mail=args["mail"],
				phone=args["phone"],
				website=args["website"],
				sic_website=args["sic_website"]
			)
			db.session.add(new_place)
			db.session.commit()

		except Exception as e:
			logger.error(f"Error creating new place: {e}. Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": GENERAL_ERROR_MESSAGE,
				"error_code": "TT.500"
			}), 500)

		logger.debug("Creating new place's address...")
		try:
			new_address: Address = Address(
				cp=args["cp"],
				street_number=args["street_number"],
				colony=args["colony"],
				municipality=args["municipality"],
				state=args["state"],
				latitude=args["latitude"],
				longitude=args["longitude"],
				how_to_arrive=args["how_to_arrive"],
				id_place=new_place.id
			)
			db.session.add(new_address)
			db.session.commit()

		except Exception as e:
			logger.error(f"Error creating new place's address: {e}. Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": GENERAL_ERROR_MESSAGE,
				"error_code": "TT.500"
			}), 500)

		logger.debug("Creating new place's review...")
		try:
			new_review: Review = Review(
				review=args["review"],
				historic_review=args["historic_review"],
				id_place=new_place.id
			)
			db.session.add(new_review)
			db.session.commit()

		except Exception as e:
			logger.error(f"Error creating new place's review: {e}. Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": GENERAL_ERROR_MESSAGE,
				"error_code": "TT.500"
			}), 500)

		logger.debug("Returning place id...")
		return make_response(jsonify({
			"status": "Success",
			"message": "Place created successfully",
			"id": new_place.id
		}), 201)


class PlaceDetail(Resource):
	@jwt_required()
	def get(self, id: int) -> Response:
		logger.debug(f"Getting place with id {id}...")

		try:
			place: Place = Place.query.get_or_404(id)

		except NotFound:
			logger.error("Place not found. Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": "Place not found",
				"error_code": "TT.D404"
			}), 404)

		except Exception as e:
			logger.error(f"Error getting place: {e}. Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": GENERAL_ERROR_MESSAGE,
				"error_code": "TT.500"
			}), 500)

		logger.debug("Serializing place...")
		try:
			result: dict[str, Any] = {
				"id": place.id,
				"info": {
					"name": place.name,
					"classification": place.classification,
					"punctuation": place.punctuation,
					"description": place.description,
					"schedules": place.schedules,
					"services": place.services,
					"activities": place.activities,
					"prices": place.prices,
					"permanent_exhibitions": place.permanent_exhibitions,
					"temporal_exhibitions": place.temporal_exhibitions,
					"mail": place.mail,
					"phone": place.phone,
					"website": place.website,
					"sic_website": place.sic_website,
				},
				"address": {
					"street_number": place.address.street_number,
					"colony": place.address.colony,
					"municipality": place.address.municipality,
					"state": place.address.state,
					"cp": place.address.cp,
					"latitude": place.address.latitude,
					"longitude": place.address.longitude,
					"how_to_arrive": place.address.how_to_arrive
				},
				"reviews": {
					"general": place.reviews.review,
					"historic": place.reviews.historic_review
				},
				"created_at": place.created_at
			}

		except Exception as e:
			logger.error(f"Error serializing place: {e}. Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": GENERAL_ERROR_MESSAGE,
				"error_code": "TT.500"
			}), 500)

		logger.debug("Returning place...")
		return make_response(jsonify({
			"status": "Success",
			"message": "Place retrieved successfully",
			"place": result
		}), 200)

	@jwt_required()
	def put(self, id: int) -> Response:
		logger.debug(f"Updating place with id {id}...")

		logger.debug("Checking request data...")
		args: Namespace = create_put_place_parser()

		logger.debug("Checking if place exists...")
		try:
			place: Place = Place.query.get_or_404(id)

		except NotFound:
			logger.error("Place not found. Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": "Place not found",
				"error_code": "TT.D404"
			}), 404)

		except Exception as e:
			logger.error(f"Error checking if place exists: {e}. Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": GENERAL_ERROR_MESSAGE,
				"error_code": "TT.500"
			}), 500)

		logger.debug("Updating place...")
		if args["name"]:
			place.name = args["name"]
		if args["classification"]:
			place.classification = args["classification"]
		if args["punctuation"]:
			place.punctuation = args["punctuation"]
		if args["description"]:
			place.description = args["description"]
		if args["schedules"]:
			place.schedules = args["schedules"]
		if args["services"]:
			place.services = args["services"]
		if args["activities"]:
			place.activities = args["activities"]
		if args["prices"]:
			place.prices = args["prices"]
		if args["permanent_exhibitions"]:
			place.permanent_exhibitions = args["permanent_exhibitions"]
		if args["temporal_exhibitions"]:
			place.temporal_exhibitions = args["temporal_exhibitions"]
		if args["mail"]:
			place.mail = args["mail"]
		if args["phone"]:
			place.phone = args["phone"]
		if args["website"]:
			place.website = args["website"]
		if args["sic_website"]:
			place.sic_website = args["sic_website"]

		if args["cp"]:
			place.address.cp = args["cp"]
		if args["street_number"]:
			place.address.street_number = args["street_number"]
		if args["colony"]:
			place.address.colony = args["colony"]
		if args["municipality"]:
			place.address.municipality = args["municipality"]
		if args["state"]:
			place.address.state = args["state"]
		if args["latitude"]:
			place.address.latitude = args["latitude"]
		if args["longitude"]:
			place.address.longitude = args["longitude"]
		if args["how_to_arrive"]:
			place.address.how_to_arrive = args["how_to_arrive"]

		if args["review"]:
			place.reviews.review = args["review"]
		if args["historic_review"]:
			place.reviews.historic_review = args["historic_review"]

		logger.debug("Committing changes...")
		try:
			db.session.commit()

		except IntegrityError as e:
			logger.error(f"Error committing changes: {e}. Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": "Place's name already exists",
				"error_code": "TT.D409"
			}), 409)

		except Exception as e:
			logger.error(f"Error committing changes: {e}. Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": GENERAL_ERROR_MESSAGE,
				"error_code": "TT.500"
			}), 500)

		logger.debug("Returning place id...")
		return make_response(jsonify({
			"status": "Success",
			"message": "Place updated successfully",
			"id": id
		}), 201)

	@jwt_required()
	def delete(self, id: int) -> Response:
		logger.debug(f"Deleting place with id {id}...")

		logger.debug("Checking if place exists...")
		try:
			place: Place = Place.query.get_or_404(id)

		except NotFound:
			logger.error("Place not found. Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": "Place not found",
				"error_code": "TT.D404"
			}), 404)

		except Exception as e:
			logger.error(f"Error checking if place exists: {e}. Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": GENERAL_ERROR_MESSAGE,
				"error_code": "TT.500"
			}), 500)

		logger.debug("Deleting place...")
		try:
			db.session.delete(place)
			db.session.commit()

		except Exception as e:
			logger.error(f"Error deleting place: {e}. Aborting request...")
			return make_response(jsonify({
				"status": "Failed",
				"message": GENERAL_ERROR_MESSAGE,
				"error_code": "TT.500"
			}), 500)

		logger.debug("Returning success message...")
		return make_response(jsonify({
			"status": "Success",
			"message": "Place deleted successfully",
		}), 200)


api.add_resource(PlaceList, '/')
api.add_resource(PlaceDetail, "/<int:id>")
