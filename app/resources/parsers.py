from flask_restful import reqparse
from flask_restful.reqparse import Namespace


###############################################################################
######################### Places Blueprints Parsers ###########################
###############################################################################

def create_get_place_parser() -> Namespace:
	parser = reqparse.RequestParser()

	parser.add_argument("classification", help="Classification field (str)")
	parser.add_argument("municipality", help="Municipality field (str)")
	parser.add_argument("distance", type=int, help="Distance field (int)")
	parser.add_argument("current_latitude", type=float, help="Current_latitude field (float)")
	parser.add_argument("current_longitude", type=float, help="Current_longitude field (float)")

	return parser.parse_args()


def create_post_place_parser() -> Namespace:
	parser = reqparse.RequestParser()

	# General fields
	parser.add_argument("name", required=True, help="Name field (str) required")
	parser.add_argument("classification", required=True, help="Classification field (str) required")
	parser.add_argument("punctuation", type=float, help="Punctuation field (float)")
	parser.add_argument("description", required=True, help="Description field (str) required")
	parser.add_argument("schedules", help="Schedules field (str)")
	parser.add_argument("services", help="Services field (str)")
	parser.add_argument("activities", help="Activities field (str)")
	parser.add_argument("prices", help="Prices field (str)")
	parser.add_argument("permanent_exhibitions", help="Permanent exhibitions field (str)")
	parser.add_argument("temporal_exhibitions", help="Temporal exhibitions field (str)")
	parser.add_argument("mail", help="Mail field (str) required")
	parser.add_argument("phone", type=int, help="Phone field (int)")
	parser.add_argument("website", help="Website field (str)")
	parser.add_argument("sic_website", help="SIC website field (str)")

	# Address fields
	parser.add_argument("cp", type=int, required=True, help="CP field (int)")
	parser.add_argument("street_number", required=True, help="Street number field (int)")
	parser.add_argument("colony", required=True, help="Colony field (str)")
	parser.add_argument("municipality", required=True, help="Municipality field (str)")
	parser.add_argument("state", required=True, help="State field (str)")
	parser.add_argument("latitude", type=float, required=True, help="Latitude field (float)")
	parser.add_argument("longitude", type=float, required=True, help="Longitude field (float)")
	parser.add_argument("how_to_arrive", help="How to arrive field (str)")

	# Review fields
	parser.add_argument("review", help="Review field (str)")
	parser.add_argument("historic_review", help="Historic review field (str)")

	return parser.parse_args()


def create_put_place_parser() -> Namespace:
	parser = reqparse.RequestParser()

	# General fields
	parser.add_argument("name", help="Name field (str) required")
	parser.add_argument("classification", help="Classification field (str) required")
	parser.add_argument("punctuation", type=float, help="Punctuation field (float)")
	parser.add_argument("description", help="Description field (str) required")
	parser.add_argument("schedules", help="Schedules field (str)")
	parser.add_argument("services", help="Services field (str)")
	parser.add_argument("activities", help="Activities field (str)")
	parser.add_argument("prices", help="Prices field (str)")
	parser.add_argument("permanent_exhibitions", help="Permanent exhibitions field (str)")
	parser.add_argument("temporal_exhibitions", help="Temporal exhibitions field (str)")
	parser.add_argument("mail", help="Mail field (str) required")
	parser.add_argument("phone", type=int, help="Phone field (int)")
	parser.add_argument("website", help="Website field (str)")
	parser.add_argument("sic_website", help="SIC website field (str)")

	# Address fields
	parser.add_argument("cp", type=int, help="CP field (int)")
	parser.add_argument("street_number", help="Street number field (int)")
	parser.add_argument("colony", help="Colony field (str)")
	parser.add_argument("municipality", help="Municipality field (str)")
	parser.add_argument("state", help="State field (str)")
	parser.add_argument("latitude", type=float, help="Latitude field (float)")
	parser.add_argument("longitude", type=float, help="Longitude field (float)")
	parser.add_argument("how_to_arrive", help="How to arrive field (str)")

	# Review fields
	parser.add_argument("review", help="Review field (str)")
	parser.add_argument("historic_review", help="Historic review field (str)")

	return parser.parse_args()


def create_get_detail_place_parser() -> Namespace:
	parser = reqparse.RequestParser()

	parser.add_argument("current_latitude", type=float, required=True, help="Current_latitude field (float)")
	parser.add_argument("current_longitude", type=float, required=True, help="Current_longitude field (float)")

	return parser.parse_args()

###############################################################################
######################### Users Blueprints Parsers ############################
###############################################################################

def create_post_user_parser() -> Namespace:
	parser = reqparse.RequestParser()

	parser.add_argument("username", required=True, help="Username field (str) required")
	parser.add_argument("mail", required=True, help="Mail field (str) required")
	parser.add_argument("password", required=True, help="Password field (str) required")

	return parser.parse_args()


def create_put_user_parser() -> Namespace:
	parser = reqparse.RequestParser()

	parser.add_argument("username", help="Username field (str)")
	parser.add_argument("mail", help="Mail field (str)")
	parser.add_argument("password", help="Password field (str)")

	return parser.parse_args()


def create_auth_user_parser() -> Namespace:
	parser = reqparse.RequestParser()

	parser.add_argument("mail", required=True, help="Mail field (str) required")
	parser.add_argument("password", required=True, help="Password field (str) required")

	return parser.parse_args()


def create_get_favorite_parser() -> Namespace:
	parser = reqparse.RequestParser()

	parser.add_argument("current_latitude", type=float, required=True, help="Current_latitude field (float)")
	parser.add_argument("current_longitude", type=float, required=True, help="Current_longitude field (float)")

	return parser.parse_args()


def create_post_favorite_parser() -> Namespace:
	parser = reqparse.RequestParser()

	parser.add_argument("user_id", type=int, required=True, help="User_id field (int) required")
	parser.add_argument("place_id", type=int, required=True, help="Place_id field (int) required")

	return parser.parse_args()


def create_post_coordinates_parser() -> Namespace:
	parser = reqparse.RequestParser()

	parser.add_argument("latitude", required=True, type=float, help="Latitude field (float) required")
	parser.add_argument("longitude", required=True, type=float, help="Longitude field (float) required")

	return parser.parse_args()

###############################################################################
######################### Models Blueprints Parsers ###########################
###############################################################################

def create_speech_recognition_model_parser() -> Namespace:
	parser = reqparse.RequestParser()

	parser.add_argument("audio", required=True, help="Audio field (str) required")

	return parser.parse_args()


def create_agent_model_parser() -> Namespace:
	parser = reqparse.RequestParser()

	parser.add_argument("prompt", required=True, help="Prompt field (str) required")
	parser.add_argument("tts", required=True, type=bool, help="Tts field (boolean) required")

	return parser.parse_args()
