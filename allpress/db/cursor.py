from psycopg2.errors import *
import psycopg2

from allpress.settings import *
from allpress.db.models import *
from allpress.lang.word import encapsulate_quotes, get_language_name_from_iso639
from allpress.exceptions import ForeignKeyWithoutReferenceError

from re import sub

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
                                reference_table=None,
                                reference_column=None) -> str:
        column_names_and_types_string = ''
        for key, val in zip(list(column_names_and_types.keys()), list(column_names_and_types.values())):
            if primary_key and key == primary_key:
                column_names_and_types_string += f'{key} {val} PRIMARY KEY,'
                continue
  
            if (foreign_key and reference_table) and (key == foreign_key):
                if reference_column:
                    column_names_and_types_string += f'{key} {val} REFERENCES {reference_table}({reference_column}),'
                else:
                    column_names_and_types_string += f'{key} {val} REFERENCES {reference_table}({foreign_key}),'
                continue
            elif foreign_key and not reference_table:
                logging.critical(f'Reference table not provided for foreign key {foreign_key}! Abort.')
                raise ForeignKeyWithoutReferenceError(f'Reference table not provided for foreign key {foreign_key}')
            column_names_and_types_string += f'{key} {val},'

    
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

    def select_rows(self,
                     table: str,
                     all=False,
                     **filters):
        pass
        
    

    @classmethod
    def create_table(self, 
                     table: str, 
                     column_names_and_types: dict,
                     primary_key=None,
                     foreign_key=None,
                     reference_table=None,
                     reference_column=None):
        creation_query = Transactions.generate_create_table_query(
                            table,
                            column_names_and_types,
                            primary_key=primary_key,
                            foreign_key=foreign_key,
                            reference_table=reference_table,
                            reference_column=reference_column)
        print(creation_query)
        db_cursor.execute(creation_query)
        postgres_database_connection.commit()


"""Migrates list of PageModel objects to the database.\n\n
pages: list (List of PageModel objects to be migrated
to the database.)
"""
def migrate_pages_to_db(pages: list[PageModel]):
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
            logging.warning('Page table is not defined in the database for pg_page. Creating.')
            logging.info('Rolling back PostgreSQL database to previous state.')
            db_cursor.execute('ROLLBACK')
            Transactions.create_table(
                table_name,
                PageModel.column_name_type_store,
                primary_key='uid',
                foreign_key='news_source',
                reference_table='pg_newssource',
                reference_column='name',)
            Transactions.insert_rows(
                table_name,
                PageModel.column_names,
                column_values
            )
        except UniqueViolation:
            logging.warning('Unique constraint violation for uid. Perhaps this page is already in the database?')
            print(f'Unique key constraint violation: {page["uid"]}. Rolling back database and skipping. Page with matching checksum already exists in this table.')
            logging.info('Rolling back PostgreSQL database to previous state.')
            db_cursor.execute('ROLLBACK')
            continue


def migrate_translations_to_db(translation_objects: list[TranslationModel]):
    for translation in translation_objects:
        table_name = f'pg_translation_{translation["translation_language"]}'
        column_values = []
        for column_name in TranslationModel.column_names:
            column_values.append(translation[column_name])
        try:
            Transactions.insert_rows(
                table_name,
                TranslationModel.column_names,
                column_values
            )
        except UndefinedTable:
            db_cursor.execute('ROLLBACK')
            Transactions.create_table(
                table_name,
                TranslationModel.column_name_type_store,
                foreign_key='uid',
                reference_table='pg_page'
            )
            Transactions.insert_rows(
                table_name,
                TranslationModel.column_names,
                column_values
            )


def migrate_states_to_db(state_objects: list[StateModel]):
    table_name = 'pg_state'
    for state in state_objects:
        column_values = []
        for column_name in StateModel.column_names:
            if column_name == 'location':
                column_values.append(str(state[column_name]).replace('[', '{').replace(']', '}'))
                continue
            column_values.append(state[column_name])
        try:
            Transactions.insert_rows(
                table_name,
                StateModel.column_names,
                column_values
            )
        except UndefinedTable:
            db_cursor.execute('ROLLBACK')
            Transactions.create_table(
                table_name,
                StateModel.column_name_type_store,
                primary_key='common_name'
            )
            Transactions.insert_rows(
                table_name,
                StateModel.column_names,
                column_values
            )
        except UniqueViolation:
            print(f'Unique key constraint violation: {state["official_name"]}. Rolling back database and skipping. State with matching official name already exists in this table.')
            db_cursor.execute('ROLLBACK')
            continue


def migrate_news_sources_to_db(news_sources: list[NewsSourceModel]):
    table_name = 'pg_newssource'
    for news_source in news_sources:
        column_values = []
        for column_name in NewsSourceModel.column_names:
            print(news_source[column_name])
            column_values.append(news_source[column_name])
        try:
            Transactions.insert_rows(
                table_name,
                NewsSourceModel.column_names,
                column_values)
        except UndefinedTable:
            db_cursor.execute('ROLLBACK')
            Transactions.create_table(
                table_name,
                NewsSourceModel.column_name_type_store,
                primary_key='name',
                foreign_key='country',
                reference_table='pg_state',
                reference_column='common_name',)
            Transactions.insert_rows(
                table_name,
                NewsSourceModel.column_names,
                column_values)
        except ForeignKeyViolation:
            db_cursor.execute('ROLLBACK')
            continue