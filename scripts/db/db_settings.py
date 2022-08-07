# -*- coding: utf-8 -*-

from pydantic import BaseSettings, PostgresDsn, validator
from typing import Dict, Any, Union, Optional
import sys
sys.path.append('./')
import scripts.other.read_write_files as working_with_file

class Settings(BaseSettings):
    parse_settings = working_with_file.load_yaml('./parse_settings.yml')
    DATABASE_USER: str=parse_settings['db_access']['user']
    DATABASE_PASSWORD: str=parse_settings['db_access']['password']
    DATABASE_HOST: str=parse_settings['db_access']['host']
    DATABASE_PORT: Union[int, str]=parse_settings['db_access']['port']
    DATABASE_NAME: str=parse_settings['db_access']['db_name']
    DATABASE_TABLE_NAME: str=parse_settings['db_access']['table_name']
    DATABASE_URI: Optional[str]

    @validator("DATABASE_URI", pre=True)
    def settings(v: Optional[str], values: Dict[str, Any]):
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql+psycopg2",
            user=values.get("DATABASE_USER"),
            password=values.get("DATABASE_PASSWORD"),
            host=values.get("DATABASE_HOST"),
            port=str(values.get("DATABASE_PORT")),
            path=f"/{values.get('DATABASE_NAME') or ''}",
        )

settings = Settings()