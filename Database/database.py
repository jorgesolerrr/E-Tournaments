from sqlalchemy import create_engine, MetaData
from Database.config import SQLALCHEMY_URL
from sqlalchemy.orm import declarative_base


engine = create_engine(SQLALCHEMY_URL, echo=True)
Base = declarative_base()
metadata_obj = MetaData()
