# -*- coding: utf-8 -*-

from sqlalchemy import create_engine, MetaData, Table, inspect, Column, Text
import migrate.changeset as migrate
import sys
sys.path.append('./')
from scripts.db.db_settings import settings
import scripts.db.db_model as model

class DB():

    def __init__(self):
        self.engine = create_engine(settings.DATABASE_URI, echo=True)
        self.inspector = inspect(self.engine)
        self.meta = MetaData(self.engine)
        if settings.DATABASE_TABLE_NAME not in self.inspector.get_table_names():
            model.table.metadata.create_all(self.engine)

        self.table = Table(settings.DATABASE_TABLE_NAME, self.meta, autoload=True)

    def create_column(self, column_name):
        column = Column(column_name, Text)
        migrate.create_column(column, table=self.table)

    def insert_data(self, data: dict):
        col_name = []
        for column in list(self.table.c):
            col_name.append(column.name)
        for d in data:
            if d not in col_name:
                self.create_column(d)
            data[d] = data[d]
        with self.engine.connect() as connect:
            connect.execute(self.table.insert(), data)
