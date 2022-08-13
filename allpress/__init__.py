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
