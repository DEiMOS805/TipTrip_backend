from sqlalchemy.engine.base import Engine
from sqlalchemy import create_engine, MetaData
from sqlalchemy.sql.schema import MetaData as MetaDataType

from app import auth
from app.resources.config import SCHEMA


@auth.verify_password
def verify(username: str, password: str) -> bool:
	""" Function that handles the logic for basic authentication """
	if not username and password:
		return False

	if username != "admin" or password != "admin":
		return False

	return True


def get_db_engine(user: str, password: str, host: str, port: int, db: str) -> Engine:
	try:
		url: str = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"
		return create_engine(url=url)
	except:
		raise Exception


def get_db_metadata(schema: str = SCHEMA) -> MetaDataType:
	try:
		return MetaData(schema=schema)
	except:
		raise Exception
