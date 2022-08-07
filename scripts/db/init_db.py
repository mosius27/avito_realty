# -*- coding: utf-8 -*-

from sqlalchemy import create_engine, MetaData, Table, Column, select, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker
from db_settings import settings
import db_model as model

engine = create_engine(settings.DATABASE_URI, echo=True)
meta = MetaData(engine)
if settings.DATABASE_TABLE_NAME not in meta:
    model.table.metadata.create_all(engine)