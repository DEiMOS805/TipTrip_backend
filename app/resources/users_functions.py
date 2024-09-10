import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet

from sqlalchemy.sql.dml import Update
from sqlalchemy.orm.query import Query
from sqlalchemy.sql import select, Delete
from sqlalchemy.engine.base import Engine
from sqlalchemy import MetaData, Table, insert, sql, update, delete, and_

from app.resources.config import DOTENV_ABSPATH
from app.resources.functions import get_db_metadata


load_dotenv(DOTENV_ABSPATH)


def encrypt(string: str) -> bytes:
	encoded: bytes = string.encode()
	f: Fernet = Fernet(os.getenv("FERNET_SECRET_KEY"))
	return f.encrypt(encoded)


def decrypt(string: str) -> str:
	f: Fernet = Fernet(os.getenv("FERNET_SECRET_KEY"))
	decrypted: bytes = f.decrypt(string)
	return decrypted.decode()


def get_add_user_query(
		engine: Engine,
		username: str,
		email: str,
		password: str,
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
			ruta_imagen_perfil=image_path
		)
	)

	return query


def get_verify_user_query(engine: Engine, email: str, get_all: bool = False) -> Query:
	metadata: MetaData = get_db_metadata()
	users_table = Table("usuarios", metadata, autoload_with=engine)

	if get_all:
		query: Query = (
			select(users_table.c.id, users_table.c.nombre, users_table.c.contraseña)
			.where(users_table.c.correo == email)
		)
	else:
		query: Query = (
			select(users_table.c.id)
			.where(users_table.c.correo == email)
		)

	return query


def get_update_user_query(
		engine: Engine,
		user_id: int,
		new_username: str | None,
		new_email: str | None,
		new_password: str | None,
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
	if new_image_path is not None:
		new_values["ruta_imagen_perfil"] = new_image_path

	query = query.values(new_values)

	return query


def get_delete_user_query(engine: Engine, user_id: int) -> Delete:
	metadata: MetaData = get_db_metadata()
	users_table = Table("usuarios", metadata, autoload_with=engine)

	query: Delete = delete(users_table).where(users_table.c.id == user_id)

	return query
