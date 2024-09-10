import os
from dotenv import load_dotenv
from sqlalchemy.engine.base import Engine
from sqlalchemy import create_engine, MetaData
from sqlalchemy.sql.schema import MetaData as MetaDataType

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


def save_as_temp_file(audio_data: bytes) -> None:
	with open(os.path.join(TEMP_ABSPATH, TEMP_FILE_NAME), "wb") as file:
		file.write(audio_data)
