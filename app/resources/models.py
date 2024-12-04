from datetime import datetime

from app.resources.database import db


class Place(db.Model):
	__tablename__: str = "places"

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(105), unique=True, nullable=False)
	classification = db.Column(db.String(20), nullable=False)
	punctuation = db.Column(db.Float)
	description = db.Column(db.Text, nullable=False)
	schedules = db.Column(db.Text)
	services = db.Column(db.Text)
	activities = db.Column(db.Text)
	prices = db.Column(db.Text)
	permanent_exhibitions = db.Column(db.Text)
	temporal_exhibitions = db.Column(db.Text)
	mail = db.Column(db.String(100))
	phone = db.Column(db.BigInteger)
	website = db.Column(db.String(150))
	sic_website = db.Column(db.String(150))
	created_at = db.Column(db.DateTime, default=datetime.utcnow)

	reviews = db.relationship("Review", backref="place", lazy=True, uselist=False)
	address = db.relationship("Address", backref="place", lazy=True, uselist=False)
	favorites = db.relationship("Favorite", backref="place", lazy=True)

	def __repr__(self) -> str:
		return f"Place(name={self.name}, classification={self.classification})"


class Review(db.Model):
	__tablename__: str = "reviews"

	id = db.Column(db.Integer, primary_key=True)
	review = db.Column(db.Text)
	historic_review = db.Column(db.Text)
	created_at = db.Column(db.DateTime, default=datetime.utcnow)

	id_place = db.Column(db.Integer, db.ForeignKey("places.id"), unique=True)

	def __repr__(self) -> str:
		return f"Review(id={self.id}, id_place={self.id_place})"


class Address(db.Model):
	__tablename__: str = "addresses"

	id = db.Column(db.Integer, primary_key=True)
	cp = db.Column(db.Integer, nullable=False)
	street_number = db.Column(db.String(100), nullable=False)
	colony = db.Column(db.String(70), nullable=False)
	municipality = db.Column(db.String(50), nullable=False)
	state = db.Column(db.String(50), nullable=False)
	latitude = db.Column(db.Float, nullable=False)
	longitude = db.Column(db.Float, nullable=False)
	how_to_arrive = db.Column(db.Text)
	created_at = db.Column(db.DateTime, default=datetime.utcnow)

	id_place = db.Column(db.Integer, db.ForeignKey("places.id"), unique=True)

	def __repr__(self) -> str:
		return f"Address(id={self.id}, id_place={self.id_place})"


class User(db.Model):
	__tablename__: str = "users"

	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(50), nullable=False)
	mail = db.Column(db.String(50), unique=True, nullable=False)
	password = db.Column(db.LargeBinary, nullable=False)
	is_admin = db.Column(db.Boolean, default=False)
	latitude = db.Column(db.Float, default=None)
	longitude = db.Column(db.Float, default=None)
	created_at = db.Column(db.DateTime, default=datetime.utcnow)

	favorites = db.relationship("Favorite", backref="user", lazy=True, cascade="all, delete-orphan")

	def __repr__(self) -> str:
		return f"User(username={self.username})"


class Favorite(db.Model):
	__tablename__: str = "favorites"

	id_place = db.Column(db.Integer, db.ForeignKey("places.id"), primary_key=True)
	id_user = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
	created_at = db.Column(db.DateTime, default=datetime.utcnow)

	def __repr__(self) -> str:
		return f"Favorite(id_place={self.id_place}, id_user={self.id_user})"
