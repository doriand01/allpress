from allpress.db import cursor
from allpress.db import models
from allpress.db import query
from allpress.lang import word
from allpress.lang import statistics
from allpress.net import web
from allpress.net import request_managers
from allpress.geo import geo
from allpress import settings
from allpress import exceptions
from allpress import util

import pycountry
import country_converter as coco
import iso639

import sys
import os

from tkinter import *
from tkinter import ttk
from functools import partial

from hashlib import md5
from psycopg2.errors import UndefinedColumn

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

import_news_sources_from_file = query.import_news_sources_from_file

def add_all_countries_to_db():
    all_countries = pycountry.countries
    
    country_models = []
    for country in all_countries:
        com_name = coco.convert([country.name], to='name_short')
        com_name = country.name
        try:
            official_name = country.official_name
        except AttributeError:
            official_name = country.name
        try:
            model = models.create_country_model(com_name)
        except Exception:
            print("Unknown error creating model. Skipping.")
            continue
        country_models.append(model)
    cursor.migrate_states_to_db(country_models)

def add_country_to_db(name: str):
    common_name = coco.convert([name], to='name_short')
    country = pycountry.countries.lookup(common_name)
    try:
        offical_name = country.official_name
    except AttributeError:
        offical_name = country.name
    model = models.create_country_model(common_name)
    cursor.migrate_states_to_db([model]) 


def add_news_sources_to_db(sources: list):
    news_models =  models.create_news_source_model(sources)
    cursor.migrate_news_sources_to_db(news_models)


def get_uid_from_url(url: str) -> str:
    page_p_data =  word.compile_p_text([url])
    hashobj = md5()
    hashobj.update(bytes(str(page_p_data).encode('utf-8')))
    uid = hashobj.hexdigest()
    return uid


def create_crawler(root_url: str, source_name: str) -> web.Crawler:
    return web.Crawler(root_url, source_name)


def add_indexed_pages_to_db(crawler: web.Crawler):
    pages = []
    translations = []
    for site in crawler.total_parsed:
        try:
            page = models.create_page_model(site, crawler.source_name)
            translation = models.create_translation_model(page)
            pages.append(page)
            translations.append(translation)
        except exceptions.NoParagraphDataError:
            continue
    cursor.migrate_pages_to_db(pages)
    cursor.migrate_translations_to_db(translations)


def select_news_source(continent=None,
                        country=None,
                        name=None,
                        headquarters=None,
                        website=None,
                        ):
    if not any([continent, country, name, headquarters, website]):
        raise exceptions.QueryError("You did not provide any values to query by. At least one is required.")
    main_query = 'SELECT * FROM pg_newssource WHERE '
    if continent: main_query += f'continent = \'{continent}\''
    if country: main_query += f'country = \'{country}\''
    if name: main_query += f'name = \'{name}\''
    if headquarters: main_query += f'headquarters = \'{headquarters}\''
    if website: main_query += f'website = \'{website}\''
    main_query += ';'
    cursor.db_cursor.execute(main_query)
    return cursor.db_cursor.fetchall()


def select_page(url=None,
                select_all=False,
                home_url=None,
                p_data=None,
                language=None,
                news_source=None,
                uid=None):
    if select_all:
        main_query = 'SELECT * FROM pg_page'
        cursor.db_cursor.execute(main_query)
        return cursor.db_cursor.fetchall()
    if not any([url, home_url, p_data, language, news_source, uid]):
        raise exceptions.QueryError("You did not provide any values to query by. At least one is required.")
    main_query = 'SELECT * FROM pg_page WHERE '
    if uid: 
        main_query += f'uid = \'{uid}\';'
        cursor.db_cursor.execute(main_query)
        return cursor.db_cursor.fetchone()
    if url: main_query += f'url = \'{url}\''
    if home_url: main_query += f'url = \'{home_url}\''
    if p_data: main_query += f'p_data = \'{p_data}\''
    if language: main_query += f'language = \'{language.upper()}\''
    if news_source: main_query += f'news_source = \'{news_source}\''
    main_query += ';'
    cursor.db_cursor.execute(main_query)
    return cursor.db_cursor.fetchall()

def search_by_text(text_query: str, language='auto') -> list:
    try:
        settings.logging.info(f"Executing search query for '{text_query}'.")
        if language == 'auto':
            language = word.detect_string_language(text_query)
            settings.logging.info(f"Language of query autodetected as {language}")
        query_results = query.execute_text_search_tsquery(text_query, language_as_iso_code=language)
        settings.logging.info(f"Found {len(query_results)} results.")
        return query_results
    except UndefinedColumn:
        cursor.db_cursor.execute('ROLLBACK')
        settings.logging.warning(f"Attempted to query tsquery against table for {language} without tsvector column")
        settings.logging.info(f"Creating tsvector column for {language}.")
        language_full_name = iso639.to_name(language).lower().split(';')[0]
        filepath = os.path.join(settings.POSTGRESQL_QUERY_PATH, f'{language_full_name}\\{language_full_name}_query_tablegen.sql')
        cursor._execute_sql_file(filepath)
        query_results = query.execute_text_search_tsquery(text_query, language_as_iso_code=language)
        settings.logging.info(f"Found {len(query_results)} results.")
        return query_results


### THIS CODE NEEDS TO BE CLEANED UP!! FIND A BETTER WAY TO DO THIS!
def graphic_search_by_text(text_query: str, language='auto'):
    query_results = search_by_text(text_query, language)
    urls = []
    for i in range(len(query_results)):
        urls.append(select_page(uid=query_results[i][1])[0])
    root = Tk()
    frame = ttk.Frame(root, padding=15)
    frame.grid()
    for i in range(len(query_results)):
        print(query_results[i][1])
        ttk.Label(frame, text=query_results[i][2]).grid(column=0, row=i)
        ttk.Label(frame, text=query_results[i][0][:32]).grid(column=1, row=i)
        ttk.Button(frame, text="Open Link", command=partial(util._open_web_url, urls[i])).grid(column=2, row=i)
    ttk.Button(frame, text="Close", command=root.destroy).grid(column=1, row=len(query_results)+1)
    ttk.Scrollbar(frame, orient='vertical').grid(column=0, row=0)
    root.mainloop()
        

