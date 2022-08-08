# -*- coding: utf-8 -*-

from sqlalchemy import create_engine, MetaData, Table, FetchedValue, inspect, Column, Integer, Text
from sqlalchemy.orm import sessionmaker, Query, query
import migrate.changeset as migrate
from db_settings import settings
import db_model as model

engine = create_engine(settings.DATABASE_URI, echo=True)
inspector = inspect(engine)
meta = MetaData(engine)
if settings.DATABASE_TABLE_NAME not in inspector.get_table_names():
    model.table.metadata.create_all(engine)

table = Table(settings.DATABASE_TABLE_NAME, meta, autoload=True)
col = Column('test', Text)
migrate.create_column(col, table=table)
...