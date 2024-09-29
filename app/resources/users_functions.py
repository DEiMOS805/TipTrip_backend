from os import getenv
from logging import getLogger
from dotenv import load_dotenv
from cryptography.fernet import Fernet

from sqlalchemy.sql.dml import Update
from sqlalchemy.orm.query import Query
from sqlalchemy.sql import select, Delete
from sqlalchemy.engine.base import Engine
from sqlalchemy import MetaData, Table, insert, sql, update, delete

from app.resources.functions import get_db_metadata
from app.resources.config import DOTENV_ABSPATH, PROJECT_NAME

load_dotenv(DOTENV_ABSPATH)
logger = getLogger(f"{PROJECT_NAME}.user_functions")


def encrypt(string: str) -> bytes:
	encoded: bytes = string.encode()
	f: Fernet = Fernet(getenv("FERNET_SECRET_KEY"))
	return f.encrypt(encoded)


def decrypt(string: str) -> str:
	f: Fernet = Fernet(getenv("FERNET_SECRET_KEY"))
	decrypted: bytes = f.decrypt(string)
	return decrypted.decode()


def get_add_user_query(
		engine: Engine,
		username: str,
		mail: str,
		password: bytes,
	) -> Query:

	logger.info("Getting metadata...")
	metadata: MetaData = get_db_metadata()
	logger.info("Conecting to users table...")
	users_table = Table("users", metadata, autoload_with=engine)

	logger.info("Creating query...")
	query: Query = (
		insert(users_table).values(
			id=sql.expression.text("DEFAULT"),
			username=username,
			mail=mail,
			password=password
		)
	)

	return query


def get_verify_user_query(engine: Engine, mail: str, get_all: bool = False) -> Query:
	metadata: MetaData = get_db_metadata()
	users_table = Table("users", metadata, autoload_with=engine)

	if get_all:
		query: Query = (
			select(
				users_table.c.id,
				users_table.c.username,
				users_table.c.password,
				users_table.c.created_at
			)
			.where(users_table.c.mail == mail)
		)
	else:
		query: Query = (
			select(users_table.c.id)
			.where(users_table.c.mail == mail)
		)

	return query


def get_update_user_query(
		engine: Engine,
		id: int,
		new_username: str | None,
		new_mail: str | None,
		new_password: bytes | None,
	) -> Update:

	metadata: MetaData = get_db_metadata()
	users_table = Table("users", metadata, autoload_with=engine)

	query: Update = update(users_table).where(users_table.c.id == id)
	new_values: dict = {}
	if new_username is not None:
		new_values["username"] = new_username
	if new_mail is not None:
		new_values["mail"] = new_mail
	if new_password is not None:
		new_values["password"] = new_password

	query = query.values(new_values)
	return query


def get_delete_user_query(engine: Engine, id: int) -> Delete:
	metadata: MetaData = get_db_metadata()
	users_table = Table("users", metadata, autoload_with=engine)
	query: Delete = delete(users_table).where(users_table.c.id == id)
	return query
