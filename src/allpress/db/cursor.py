from psycopg2.errors import *
import psycopg2

from allpress.settings import *
from allpress.db.models import PageModel, TranslationModel
from allpress.lexical import encapsulate_quotes
from allpress.exceptions import ForeignKeyWithoutReferenceError

### THIS VARIABLE SHOULD NOT CONTAIN LITERAL VALUES. CHANGE THE
### VALUES IN SETTINGS.PY.
postgres_database_connection = psycopg2.connect(
    host=POSTGRESQL_SERVER_HOST,
    database=POSTGRESQL_DATABASE_NAME,
    user=POSTGRESQL_USERNAME,
    password=POSTGRESQL_PASSWORD
)

db_cursor = postgres_database_connection.cursor()


class Transactions:


    """Generates a query to create a new table in the database. \n\n
table name: str (Name of table to be created) \n
column_names_and_types: dict (Key-value dictionary containing
tha name of every column and the column's datatype. Refer to
allpress.db.models.Model classes.) \n
**primary_key: str (Sets primary key in table. Optional argument.) \n
**foreign_key: str (Sets foreign keys in table. Optional argument.) \n
**reference_table: (Sets reference table for foreign key. Optional
argument, but required when foreign_key is used, or will raise 
ForeignKeyWithoutReferenceError.)
"""
    @classmethod
    def generate_create_table_query(self,
                                table_name: str, 
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
    

    """Generates an insertion query for a single row.  \n\n
    table_name: str (The name of the table to be modified) \n
    column_names: list (Names of the columns in the table to be modified) \n
    values: list (Values to be inserted into the table)
    """
    @classmethod
    def generate_insertion_query(self, table_name: str, column_names=[], values=[]) -> str:
        return f'INSERT INTO {table_name} ({", ".join(column_names)}) VALUES ({", ".join(values) });'

    
    @classmethod
    def insert_rows(self, table: str, column_names: list, values: list):
        encapsulated_values = [encapsulate_quotes(val) for val in values]
        insert_query = Transactions.generate_insertion_query(
                            table,
                            column_names,
                            encapsulated_values)
        db_cursor.execute(insert_query)
        postgres_database_connection.commit()
    

    @classmethod
    def create_table(self, 
                     table: str, 
                     column_names_and_types: dict,
                     primary_key=None,
                     foreign_key=None,
                     reference_table=None):
        creation_query = Transactions.generate_create_table_query(
                            table,
                            column_names_and_types,
                            primary_key=primary_key,
                            foreign_key=foreign_key,
                            reference_table=reference_table,)
        db_cursor.execute(creation_query)
        postgres_database_connection.commit()






    

"""Migrates list of PageModel objects to the database.\n\n
pages: list (List of PageModel objects to be migrated
to the database.)
"""
def migrate_pages_to_db(pages: list):
    table_name = 'pg_page'
    for page in pages:
        column_values = []
        for column_name in PageModel.column_names:
            column_values.append(page[column_name])
        try:
            Transactions.insert_rows(
                table_name,
                PageModel.column_names,
                column_values
            )
        except UndefinedTable:
            db_cursor.execute('ROLLBACK')
            Transactions.create_table(
                table_name,
                PageModel.column_name_type_store,
                primary_key='uid'
            )
            Transactions.insert_rows(
                table_name,
                PageModel.column_names,
                column_values
            )



def migrate_translations_to_db(translation_objects: list):
    table_name = 'pg_translation'