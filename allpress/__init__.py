from inspect import Attribute
from itertools import count
from allpress.db import cursor
from allpress.db import models
from allpress.db import io
from allpress.lexical import word
from allpress.lexical import statistics
from allpress import web
from allpress import settings
from allpress import exceptions

import pycountry
import country_converter as coco

import sys
import os
from hashlib import md5

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

import_news_sources_from_file = io.import_news_sources_from_file

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
    news_models =  models.create_news_source_model(sources)[1:]
    cursor.migrate_news_sources_to_db(news_models)


def get_uid_from_url(url: str) -> str:
    page_p_data =  word.compile_p_text(url)
    hashobj = md5()
    hashobj.update(bytes(str(word.remove_fragment(url)+page_p_data).encode('utf-8')))
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
                home_url=None,
                p_data=None,
                language=None,
                news_source=None,
                uid=None):
    if not any([url, home_url, p_data, language, news_source, uid]):
        raise exceptions.QueryError("You did not provide any values to query by. At least one is required.")
    main_query = 'SELECT * FROM pg_page WHERE '
    if uid: 
        main_query += f'uid = \'uid\';'
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
    