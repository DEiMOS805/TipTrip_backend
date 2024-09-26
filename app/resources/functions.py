import os
from dotenv import load_dotenv
from sqlalchemy.engine.base import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import create_engine, MetaData
from sqlalchemy.sql.schema import MetaData as MetaDataType

from app.resources.config import *


load_dotenv(DOTENV_ABSPATH)


def get_db_engine(url: str = os.getenv("DB_URL")) -> Engine:
	try:
		if not url:
			raise ValueError("DB_URL")
		return create_engine(url=url)
	except SQLAlchemyError as e:
		raise SQLAlchemyError("engine")
	except Exception as e:
		raise Exception(f"Error: {e}")


def get_db_metadata(schema: str = os.getenv("DB_SCHEMA")) -> MetaDataType:
	try:
		if not schema:
			raise ValueError("DB_SCHEMA")
		return MetaData(schema=schema)
	except SQLAlchemyError as e:
		raise SQLAlchemyError("metadata")
	except Exception as e:
		raise Exception(f"Error: {e}")


def save_as_temp_file(audio_data: bytes) -> None:
	with open(os.path.join(TEMP_ABSPATH, TEMP_FILE_NAME), "wb") as file:
		file.write(audio_data)
