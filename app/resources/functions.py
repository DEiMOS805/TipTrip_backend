import os
from dotenv import load_dotenv
from sqlalchemy.engine.base import Engine
from sqlalchemy import create_engine, MetaData
from sqlalchemy.sql.schema import MetaData as MetaDataType

from app.resources.config import *


load_dotenv(DOTENV_ABSPATH)


def get_db_engine(url: str = os.getenv("DB_URL")) -> Engine:
	return create_engine(url=url, connect_args={"client_encoding": "utf8"})


def get_db_metadata(schema: str = os.getenv("DB_SCHEMA")) -> MetaDataType:
	return MetaData(schema=schema)
