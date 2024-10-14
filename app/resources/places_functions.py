from sqlalchemy.sql import select
from sqlalchemy.orm.query import Query
from sqlalchemy.engine.base import Engine
from sqlalchemy import MetaData, Table, and_

from app.resources.functions import get_db_metadata


def get_demo_data_query(engine: Engine, category: str, municipality: str) -> Query:
	metadata: MetaData = get_db_metadata()
	places_table = Table("places", metadata, autoload_with=engine)
	addresses_table = Table("addresses", metadata, autoload_with=engine)

	query: Query = (
		select(
			places_table.c.name,
			places_table.c.classification,
			places_table.c.punctuation,
			addresses_table.c.street_number,
			addresses_table.c.colony,
			addresses_table.c.municipality,
			addresses_table.c.state,
			addresses_table.c.cp,
			addresses_table.c.latitude,
			addresses_table.c.longitude,
		)
		.outerjoin(
			addresses_table, places_table.c.id == addresses_table.c.id_place
		)
	)

	filters: list = []
	if category is not None:
		filters.append(places_table.c.classification == category)
	if municipality is not None:
		filters.append(addresses_table.c.municipality == municipality)

	if filters:
		query = query.where(and_(*filters))

	return query


def get_place_full_data_query(engine: Engine, name: str) -> Query:
	metadata: MetaData = get_db_metadata()
	places_table = Table("places", metadata, autoload_with=engine)
	addresses_table = Table("addresses", metadata, autoload_with=engine)
	reviews_table = Table("reviews", metadata, autoload_with=engine)

	query: Query = (
		select(
			places_table.c.name,
			places_table.c.classification,
			places_table.c.punctuation,
			places_table.c.description,
			places_table.c.schedules,
			places_table.c.services,
			places_table.c.activities,
			places_table.c.prices,
			places_table.c.permanent_exhibitions,
			places_table.c.temporal_exhibitions,
			places_table.c.mail,
			places_table.c.phone,
			places_table.c.website,
			places_table.c.sic_website,
			addresses_table.c.cp,
			addresses_table.c.street_number,
			addresses_table.c.colony,
			addresses_table.c.municipality,
			addresses_table.c.state,
			addresses_table.c.latitude,
			addresses_table.c.longitude,
			addresses_table.c.how_to_arrive,
			reviews_table.c.review,
			reviews_table.c.historic_review
		)
		.outerjoin(addresses_table, places_table.c.id == addresses_table.c.id_place)
		.outerjoin(reviews_table, places_table.c.id == reviews_table.c.id_place)
		.where(places_table.c.name == name)
	)

	return query
