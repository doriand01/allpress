import csv
import iso639

from allpress.db import cursor
from allpress import settings



def import_news_sources_from_file(filepath: str) -> list:
    csvfile = open(filepath, 'r', newline='')
    csv_reader = csv.reader(csvfile)
    csv_values = []
    for line in csv_reader:
        csv_values.append(line)
    return csv_values[1:]


def execute_text_search_tsquery(text: str, language_as_iso_code=None) -> list:
    language_real_name =  iso639.to_name(language_as_iso_code).lower()
    tsquery_filepath = settings.POSTGRESQL_QUERY_PATH + '\\' + f'{language_real_name}\\{language_real_name}_websearch_tsquery.sql'
    tsquery_sqlfile = open(tsquery_filepath, 'r')
    tsquery = tsquery_sqlfile.read()
    tsquery_sqlfile.close()
    formatted_tsquery = tsquery.replace('QUERYVAL', f'$${text}$$')
    cursor.db_cursor.execute(formatted_tsquery)
    return cursor.db_cursor.fetchall()

    
