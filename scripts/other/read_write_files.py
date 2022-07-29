# -*- coding: utf-8 -*-

import yaml
import json
import csv
from openpyxl import Workbook, load_workbook
import logging
import psycopg2

def initLogger(path: str, logLvl: str):
    import multiprocessing
    with open(path, 'w', encoding='utf-8') as file: pass

    logger = logging.getLogger(__name__)
    formatter= logging.Formatter('{processName} | log time - %(asctime)s | log level - %(levelname)s | [%(filename)s: line - %(lineno)d in function %(funcName)s] | %(message)s'.format(processName=multiprocessing.current_process().name), datefmt='%Y-%m-%d %H:%M:%S')

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logLvl.upper())
    logger.addHandler(console_handler)

    file_handler = logging.FileHandler(filename=path, encoding='utf-8')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logLvl.upper())
    logger.addHandler(file_handler)

    console_handler.setLevel(logLvl.upper())
    file_handler.setLevel(logLvl.upper())
    logger.setLevel(logLvl.upper())

    return logger

def read_txt(path: str):
    var = []
    with open(path, 'r', encoding='utf-8') as file:
        for line in file: var.append(line.replace('\n', ''))
    return var

def write_list_in_txt(path: str, var: list):
    with open(path, 'w', encoding='utf-8') as file:
        for element in var: file.write(f'{element}\n')

def create_txt(path):
    with open(path, 'w', encoding='utf-8') as file: pass

def create_csv(path, fieldnames):
    with open(path, 'w', encoding='utf-8', newline='') as file: 
        writer = csv.DictWriter(file, fieldnames=fieldnames.split(';'), delimiter=';', skipinitialspace=True, dialect = 'excel')
        writer.writeheader()

def write_csv(path: str, var: dict, fieldnames: str):
    with open(path, 'a', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames.split(';'), delimiter=';', skipinitialspace=True, dialect = 'excel')
        writer.writerow(var)

def create_excel(path: str):
    workbook = Workbook()
    workbook.save(path)

def write_line_excel(path: str, var: str, num_row: int=None):
    workbook = load_workbook(path)
    worksheet = workbook.active
    if num_row != None:
        line = var.split(';')
        col = 1
        for value in line:
            worksheet.cell(row=num_row, column=col, value=value)
            col += 1
    else: worksheet.append(var.split(';'))
    workbook.save(path)

def load_yaml(path: str):
    with open(path, 'r', encoding='utf-8') as file: return yaml.load(file, Loader=yaml.FullLoader)

def read_json(path: str):
    with open(path, 'r', encoding='utf-8') as file: return json.load(file)

def write_json(path: str, var: list or dict):
    with open(path, 'w', encoding='utf8') as file: json.dump(var, file, indent='\t', ensure_ascii=False)

def check_exists_collumn_postgresSQL(settings, var: str):
    try:
        connection = psycopg2.connect(
            host=settings['host'],
            port=settings['port'],
            user=settings['user'],
            password=settings['password'],
            database=settings['db_name']
        )

        connection.autocommit = True

        with connection.cursor() as cursor:
            cursor.execute(
                f"""SELECT EXISTS (SELECT column_name
                    FROM information_schema.columns 
                    WHERE table_name='{settings['table_name']}' AND column_name='{var}');
                    """
            )
            return cursor.fetchone()[0]
    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL", _ex)
    finally:
        if connection:
            connection.close()
            print("[INFO] PostgreSQL connection closed")

def create_table_PostgresSQL(settings, var: dict):
    try:
        connection = psycopg2.connect(
            host=settings['host'],
            port=settings['port'],
            user=settings['user'],
            password=settings['password'],
            database=settings['db_name']
        )

        connection.autocommit = True
        with connection.cursor() as cursor:
            cursor.execute(
                f"""CREATE tABLE IF NOT EXISTS test(
                    id serial PRIMARY KEY,
                    {var.date_published} timestamp,
                    {var.title} text,
                    {var.type_realty} text,
                    {var.description} text,
                    {var.price} integer,
                    {var.region} text,
                    {var.city} text,
                    {var.address} text,
                    {var.url} text,
                    {var.urls_image} text);
                """
            )
            
            print("[INFO] Table created successfully")
    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL", _ex)
    finally:
        if connection:
            connection.close()
            print("[INFO] PostgreSQL connection closed")

def insert_table_PostgresSQL(settings, var: dict, params: dict):
    try:
        connection = psycopg2.connect(
            host=settings['host'],
            port=settings['port'],
            user=settings['user'],
            password=settings['password'],
            database=settings['db_name']
        )

        var = dict(var)
        connection.autocommit = True

        for param in params:
            var[param] = params[param]

        keys = values = ''
        for v in var:
            keys += f'{v},'
            values += f"'{var[v]}',"

        if keys[-1] == ',':
            keys = keys[:-1]
        if values[-1] == ',':
            values = values[:-1]

        with connection.cursor() as cursor:
            cursor.execute(f"INSERT INTO {settings['table_name']} ({keys}) VALUES({values});")
            
            print("[INFO] Data was successfully inserted")

    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL", _ex)
    finally:
        if connection:
            connection.close()
            print("[INFO] PostgreSQL connection closed")

def add_column_PostgresSQL(settings, var: str):
    try:
        connection = psycopg2.connect(
            host=settings['host'],
            port=settings['port'],
            user=settings['user'],
            password=settings['password'],
            database=settings['db_name']
        )
        
        connection.autocommit = True

        with connection.cursor() as cursor:
            cursor.execute(
                f"ALTER TABLE {settings['table_name']} ADD COLUMN {var} text")

    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL", _ex)
    finally:
        if connection:
            connection.close()
            print("[INFO] PostgreSQL connection closed")