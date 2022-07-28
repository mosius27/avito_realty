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

def write_postgres_db(settings, var: dict or str):
    try:
        connection = psycopg2.connect(
            host=settings['host'],
            port=settings['port'],
            user=settings['user'],
            password=settings['password'],
            database=settings['db_name']
        )

        connection.autocommit = True

        # with connection.cursor() as cursor:
        #     cursor.execute(
        #         "SELECT version();"
        #     )

        #     print(f'Server version: {cursor.fetchone()}')

        # with connection.cursor() as cursor:
        #     cursor.execute(
        #         "DROP TABLE IF EXISTS test"
        #     )
        # print("[INFO] Table drop successfully")

        # with connection.cursor() as cursor:
        #     cursor.execute(
        #         """CREATE TABLE test(
        #             id serial PRIMARY KEY,
        #             date_published date,
        #             title text,
        #             type_realty text,
        #             description text,
        #             price integer,
        #             region text,
        #             city text,
        #             address text,
        #             url text,
        #             urls_image text);
        #         """
        #     )
            
        #     print("[INFO] Table created successfully")

        # with connection.cursor() as cursor:
        #     cursor.execute(
        #         """INSERT INTO test(
        #             title,
        #             type_realty,
        #             description,
        #             price,
        #             region,
        #             city,
        #             address,
        #             url,
        #             urls_image) VALUES ('QWE', 'qwe', 'asd', 1, 'ASD', 'ewq', 'EWQ', 'w', 't');
        #         """
        #     )
            
        #     print("[INFO] Data was successfully inserted")

        with connection.cursor() as cursor:
            cursor.execute(
                """SELECT EXISTS (SELECT column_name
                    FROM information_schema.columns 
                    WHERE table_name='test' AND column_name='param');
                    """
            )

        with connection.cursor() as cursor:
            cursor.execute(
                "ALTER TABLE test ADD COLUMN param text"
            )

        
    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL", _ex)
    finally:
        if connection:
            connection.close()
            print("[INFO] PostgreSQL connection closed")