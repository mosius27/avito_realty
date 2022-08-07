# -*- coding= utf-8 -*-

from sqlalchemy import Column, Integer, Text, DateTime, create_engine, MetaData, Text
from db_settings import settings
from sqlalchemy.orm import declarative_base

table = declarative_base()

class Base_Data(table):
    __tablename__ = settings.DATABASE_TABLE_NAME
    Id= Column (Integer, primary_key=True, autoincrement=True)
    Дата_публикации= Column(DateTime)
    Заголовок= Column(Text)
    Тип_недвижимости= Column(Text)
    Описание= Column(Text)
    Цена= Column(Integer)
    Регион= Column(Text)
    Город= Column(Text)
    Адрес= Column(Text)
    Url= Column(Text)
    Изображения= Column(Text)