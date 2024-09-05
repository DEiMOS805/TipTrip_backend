import os
import wave
import json
# import torch
# import numpy as np
# from TTS.api import TTS
from pyaudio import paInt16
from base64 import b64encode
from dotenv import load_dotenv
from IPython.display import Audio
from vosk import Model, KaldiRecognizer
# from scipy.signal import butter, lfilter

from sqlalchemy.orm import aliased
from sqlalchemy.sql.dml import Update
from sqlalchemy.orm.query import Query
from sqlalchemy.engine.base import Engine
from sqlalchemy.sql import func, select, Delete
from sqlalchemy.sql.selectable import Subquery, Alias
from sqlalchemy.sql.schema import MetaData as MetaDataType
from sqlalchemy import (
	create_engine, MetaData, Table, sql, and_, insert, case, update, delete
)

from app.resources.config import *


load_dotenv(DOTENV_ABSPATH)


def get_db_engine() -> Engine:
	try:
		url: str = os.getenv("DB_URL")
		return create_engine(url=url)
	except:
		raise Exception


def get_db_metadata(schema: str = os.getenv("DB_SCHEMA")) -> MetaDataType:
	try:
		return MetaData(schema=schema)
	except:
		raise Exception


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
			sites_table.c.clasificacion_arte,
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


def get_add_user_query(
		engine: Engine,
		username: str,
		email: str,
		password: str,
		role: str | None,
		image_path: str | None,
	) -> Query:

	metadata: MetaData = get_db_metadata()
	users_table = Table("usuarios", metadata, autoload_with=engine)

	query: Query = (
		insert(users_table).values(
			id=sql.expression.text("DEFAULT"),
			nombre=username,
			correo=email,
			contraseña=password,
			rol=role,
			ruta_imagen_perfil=image_path
		)
	)

	return query


def get_update_user_query(
		engine: Engine,
		user_id: int,
		new_username: str | None,
		new_email: str | None,
		new_password: str | None,
		new_role: str | None,
		new_image_path: str | None,
	) -> Update:

	metadata: MetaData = get_db_metadata()
	users_table = Table("usuarios", metadata, autoload_with=engine)

	query: Update = update(users_table).where(users_table.c.id == user_id)

	new_values: dict = {}
	if new_username is not None:
		new_values["nombre"] = new_username
	if new_email is not None:
		new_values["correo"] = new_email
	if new_password is not None:
		new_values["contraseña"] = new_password
	if new_role is not None:
		new_values["rol"] = new_role
	if new_image_path is not None:
		new_values["ruta_imagen_perfil"] = new_image_path

	query = query.values(new_values)

	return query


def get_delete_user_query(engine: Engine, user_id: int) -> Delete:
	metadata: MetaData = get_db_metadata()
	users_table = Table("usuarios", metadata, autoload_with=engine)

	query: Delete = delete(users_table).where(users_table.c.id == user_id)

	return query


def get_verify_user_query(engine: Engine, email: str, password: str = None) -> Query:
	metadata: MetaData = get_db_metadata()
	users_table = Table("usuarios", metadata, autoload_with=engine)

	if password:
		query: Query = (
			select(users_table.c.id, users_table.c.nombre)
			.where(
				and_(
					users_table.c.correo == email,
					users_table.c.contraseña == password
				)
			)
		)
	else:
		query: Query = (
			select(users_table.c.id)
			.where(users_table.c.correo == email)
		)

	return query


def save_as_temp_file(audio_data: bytes) -> None:
	with open(os.path.join(TEMP_ABSPATH, TEMP_FILE_NAME), "wb") as file:
		file.write(audio_data)


def speech_recognition() -> str:
	with wave.open(os.path.join(TEMP_ABSPATH, TEMP_FILE_NAME), "rb") as file:
		if not any([
			file.getnchannels() != CHANNELS,
			file.getsampwidth() != paInt16,
			file.getframerate() != SAMPLING_RATE
		]):
			raise ValueError("vosk_audio_file")

		model = Model(model_path=VOSK_ABSPATH)
		recognizer = KaldiRecognizer(model, SAMPLING_RATE)

		results = []
		while True:
			data = file.readframes(FRAMES_FLOW)
			if len(data) == 0:
				break
			if recognizer.AcceptWaveform(data):
				result = recognizer.Result()
				results.append(json.loads(result))

		final_result = recognizer.FinalResult()
		results.append(json.loads(final_result))

		text: str = f"{' '.join([res['text'] for res in results])}."
		return text


def tts_func(prompt: str) -> str:
# 	tts = TTS(model_name=TTS_MODEL_NAME, progress_bar=False).to(DEVICE)
# 	tts.tts_to_file(
# 		prompt,
# 		speaker_wav="my/cloning/audio.wav",
# 		file_path=join(TEMP_ABSPATH, TEMP_FILE_NAME)
# 	)

# 	with wave.open(join(TEMP_ABSPATH, TEMP_FILE_NAME), "rb") as file:
# 		audio = file.readframes(file.getnframes())
# 		audio_data: str = b64encode(audio).decode("utf-8")
# 		return audio_data
	return "None"
