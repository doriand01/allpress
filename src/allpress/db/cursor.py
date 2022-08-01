
from allpress.settings import *
from allpress.db.models import PageModel
from allpress.lexical import _encapsulate_quotes

from psycopg2.errors import *

import psycopg2



postgres_database_connection = psycopg2.connect(
    host=POSTGRESQL_SERVER_HOST,
    database=POSTGRESQL_DATABASE_NAME,
    user=POSTGRESQL_USERNAME,
    password=POSTGRESQL_PASSWORD
)

db_cursor = postgres_database_connection.cursor()
insertion_query_lam = lambda table_name, column_names=[], values=[] : f'INSERT INTO {table_name} ({", ".join(column_names)}) VALUES ({", ".join(values) });'
create_table_query_lam = lambda table_name : f'CREATE TABLE {table_name};'


def generate_insertion_query(table_name: str, column_names=[], values=[]) -> str:
    return f'INSERT INTO {table_name} ({", ".join(column_names)}) VALUES ({", ".join(values) });'

def generate_create_table_query(table_name: str, column_names_and_types: dict) -> str:
    column_names_and_types_string = str()
    for key, val in zip(list(column_names_and_types.keys()), list(column_names_and_types.values())):
        column_names_and_types_string = column_names_and_types_string + f'{key} {val},'
    return f'CREATE TABLE {table_name} ({column_names_and_types_string[:-1]})'

def migrate_pages_to_db(pages: list):
    table_name = 'pg_page'
    for page in pages:
        try:
            column_values = []
            for column_name in PageModel.column_names:
                column_values.append(page[column_name])

            insert_query = generate_insertion_query(
                table_name,
                PageModel.column_names,
                column_values
            )
            print(insert_query)
            db_cursor.execute(insert_query)
            postgres_database_connection.commit()
        except UndefinedTable:
            db_cursor.execute('ROLLBACK')
            create_table_query = generate_create_table_query(table_name,  PageModel.column_name_type_store)
            db_cursor.execute(create_table_query)
            column_values = []
            for column_name in PageModel.column_names:
                column_values.append(page[column_name])
            insert_query = generate_insertion_query(
                table_name,
                PageModel.column_names,
                column_values
            )
            db_cursor.execute(insert_query) 
            postgres_database_connection.commit()
