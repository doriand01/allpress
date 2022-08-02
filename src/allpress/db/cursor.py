from psycopg2.errors import *
import psycopg2

from allpress.settings import *
from allpress.db.models import PageModel
from allpress.lexical import encapsulate_quotes
from allpress.exceptions import ForeignKeyWithoutReferenceError

postgres_database_connection = psycopg2.connect(
    host=POSTGRESQL_SERVER_HOST,
    database=POSTGRESQL_DATABASE_NAME,
    user=POSTGRESQL_USERNAME,
    password=POSTGRESQL_PASSWORD
)

db_cursor = postgres_database_connection.cursor()


def generate_insertion_query(table_name: str, column_names=[], values=[]) -> str:
    return f'INSERT INTO {table_name} ({", ".join(column_names)}) VALUES ({", ".join(values) });'

def generate_create_table_query(table_name: str, 
                                column_names_and_types: dict, 
                                primary_key=None, 
                                foreign_key=None,
                                reference_table=None) -> str:
    column_names_and_types_string = str()
    for key, val in zip(list(column_names_and_types.keys()), list(column_names_and_types.values())):
        if primary_key and key == primary_key:
                column_names_and_types_string = column_names_and_types_string + f'{key} {val} PRIMARY KEY,'
                continue
        column_names_and_types_string = column_names_and_types_string + f'{key} {val},'
        if foreign_key and reference_table:
            constraint_string = f' CONSTRAINT fk_{reference_table} FOREIGN KEY({foreign_key}) REFERENCES {reference_table}({foreign_key})'
            return f'CREATE TABLE {table_name} ({column_names_and_types_string[:-1]})' + constraint_string
        elif foreign_key and not reference_table:
            raise ForeignKeyWithoutReferenceError(f'Reference table not provided for foreign key {foreign_key}')

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
            create_table_query = generate_create_table_query(table_name,
                                                             PageModel.column_name_type_store,
                                                             primary_key='uid')
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
