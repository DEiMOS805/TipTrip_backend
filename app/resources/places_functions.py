from sqlalchemy.orm import aliased
from sqlalchemy.orm.query import Query
from sqlalchemy.sql import select, func
from sqlalchemy.engine.base import Engine
from sqlalchemy import MetaData, Table, and_, case
from sqlalchemy.sql.selectable import Subquery, Alias

from app.resources.functions import get_db_metadata


def get_demo_data_query(engine: Engine, category: str, municipality: str) -> Query:
	metadata: MetaData = get_db_metadata()
	sites_table = Table("sitios_turisticos", metadata, autoload_with=engine)
	images_table = Table("imagenes", metadata, autoload_with=engine)
	addresses_table = Table("direcciones", metadata, autoload_with=engine)

	subquery: Subquery = (
		select(
			images_table.c.id_sitio,
			images_table.c.ruta,
			func.row_number().over(
				partition_by=images_table.c.id_sitio,
				order_by=images_table.c.id
			).label("rn")
		).subquery()
	)

	alias_subquery: Alias = aliased(subquery)

	query: Query = (
		select(
			sites_table.c.nombre,
			sites_table.c.clasificacion_sitio,
			sites_table.c.puntuacion,
			addresses_table.c.calle_numero,
			addresses_table.c.colonia,
			addresses_table.c.delegacion_municipio,
			addresses_table.c.entidad_federativa,
			addresses_table.c.cp,
			alias_subquery.c.ruta
		)
		.outerjoin(
			addresses_table, sites_table.c.id == addresses_table.c.id_sitio
		)
		.outerjoin(
			alias_subquery,
			(sites_table.c.id == alias_subquery.c.id_sitio) &\
			(alias_subquery.c.rn == 1)
		)
	)

	filters: list = []
	if category is not None:
		filters.append(sites_table.c.clasificacion_sitio == category)
	if municipality is not None:
		filters.append(addresses_table.c.delegacion_municipio == municipality)

	if filters:
		query = query.where(and_(*filters))

	return query


def get_place_full_data_query(engine: Engine, place_name: str) -> Query:
	metadata: MetaData = get_db_metadata()
	sites_table = Table("sitios_turisticos", metadata, autoload_with=engine)
	images_table = Table("imagenes", metadata, autoload_with=engine)
	addresses_table = Table("direcciones", metadata, autoload_with=engine)
	reviews_table = Table("reseñas", metadata, autoload_with=engine)

	subquery: Subquery = (
		select(
			images_table.c.id_sitio,
			images_table.c.ruta,
			func.row_number().over(
				partition_by=images_table.c.id_sitio,
				order_by=images_table.c.id
			).label("rn")
		).subquery()
	)

	alias_subquery: Alias = aliased(subquery)

	pivot_query = (
		select(
			alias_subquery.c.id_sitio,
			func.max(case((alias_subquery.c.rn == 1, alias_subquery.c.ruta))).label("ruta1"),
			func.max(case((alias_subquery.c.rn == 2, alias_subquery.c.ruta))).label("ruta2"),
			func.max(case((alias_subquery.c.rn == 3, alias_subquery.c.ruta))).label("ruta3"),
			func.max(case((alias_subquery.c.rn == 4, alias_subquery.c.ruta))).label("ruta4"),
			func.max(case((alias_subquery.c.rn == 5, alias_subquery.c.ruta))).label("ruta5"),
		).group_by(alias_subquery.c.id_sitio).subquery()
	)

	query: Query = (
		select(
			sites_table.c.nombre,
			sites_table.c.clasificacion_sitio,
			sites_table.c.puntuacion,
			sites_table.c.descripcion,
			sites_table.c.horario,
			sites_table.c.servicios,
			sites_table.c.actividades,
			sites_table.c.costos,
			sites_table.c.salas_permanentes,
			sites_table.c.salas_temporales,
			sites_table.c.email,
			sites_table.c.telefono,
			sites_table.c.extension,
			sites_table.c.pagina_web,
			sites_table.c.pagina_sic,
			addresses_table.c.calle_numero,
			addresses_table.c.colonia,
			addresses_table.c.delegacion_municipio,
			addresses_table.c.entidad_federativa,
			addresses_table.c.cp,
			addresses_table.c.latitud,
			addresses_table.c.longitud,
			addresses_table.c.referencias,
			pivot_query.c.ruta1,
			pivot_query.c.ruta2,
			pivot_query.c.ruta3,
			pivot_query.c.ruta4,
			pivot_query.c.ruta5,
			reviews_table.c.reseña_general,
			reviews_table.c.reseña_historica
		)
		.outerjoin(addresses_table, sites_table.c.id == addresses_table.c.id_sitio)
		.outerjoin(reviews_table, sites_table.c.id == reviews_table.c.id_sitio)
		.outerjoin(pivot_query, sites_table.c.id == pivot_query.c.id_sitio)
		.where(sites_table.c.nombre == place_name)
	)

	return query
