from hashlib import md5
from os import urandom

import geopy
import country_converter as coco
from time import sleep

from allpress.lang.word import *
from allpress.exceptions import TranslationError, NoSuchColumnError
from allpress.settings import logging

logging.getLogger(__name__)


class Model:

    def __init__(self, **columns):
        for name, value in zip(columns.keys(), columns.values()):
            setattr(self, f'pg_{self.__class__.__name__.lower().replace("model", "")}_{name}', value)

    def __repr__(self):
        return self.__str__()

    def __getitem__(self, val):
        return getattr(self, f'pg_{self.__class__.__name__.lower().replace("model", "")}_{val}')

"""
`PageModel` is the class which models the `page` table in the Postgres database.
The page model contains columns which encapsulate the following data relating to
each indexed page: its url, the root url of the website, the `<p>` tag data
contained within the table, the language of the page, and translations for that
page.
"""
class PageModel(Model):

    column_name_type_store = {
        'url'          : 'varchar(2048)',
        'home_url'     : 'varchar(2048)',
        'p_data'       : 'text',
        'language'     : 'varchar(10)',
        'news_source'  : 'varchar(128)',
        'uid'          : 'varchar(64)',
    }
    column_names = [
        'url', 'home_url',
        'p_data', 'language',
        'news_source', 'uid'
    ]
    def __init__(self, **columns):
        super().__init__(**columns)
        hashobj = md5()
        hashobj.update(bytes(str(remove_fragment(self.pg_page_url)+self.pg_page_p_data).encode('utf-8')))
        uid = hashobj.hexdigest()
        self.pg_page_uid = uid

    def __str__(self):
        return f'<{self.pg_page_url}; {self.pg_page_language}...>'


"""
`TranslationModel` is the class which models the `translation` table in the Postgres 
database. The translation model contains columns which encapsulate the following data 
relating to each translations in the text of each indexed page: the page's uid in the
database, the text of the translation, the language of the translation, if the
translation is the original translation of the text, and if it is an offical,
human verified translation.
"""
class TranslationModel(Model):
    
    column_name_type_store = {
        'uid'                  : 'varchar(64)',
        'translation_text'     : 'text',
        'translation_language' : 'varchar(10)',
        'is_original'          : 'boolean',
        'is_official'          : 'boolean',
    }
    column_names = [
        'uid',
        'translation_text',
        'translation_language',
        'is_original',
        'is_official',
    ]
    def __init__(self, **columns):
        super().__init__(**columns)

    def __str__(self):
        return f'<Translation of {self.pg_translation_page_uid[:5]}, Lang:{self.pg_translation_translation_language}>'




class StateModel(Model):

    column_name_type_store = {
        'official_name'   :  'varchar(256)',
        'common_name'    :  'varchar(64)',
        'location'       :  'real[2]'
    }
    column_names = [
        'official_name',
        'common_name',
        'location'
    ]

    def __init__(self, **columns):
        super().__init__(**columns)
        

    def __str__(self):
        return f'<Country: {self.pg_state_official_name}, location, {self.pg_state_location}>'


class NewsSourceModel(Model):

    column_name_type_store = {
        'continent'   : 'varchar(24)',
        'country'     : 'varchar(256)',
        'name'        : 'varchar(128)',
        'headquarters': 'varchar(24)',
        'website'     : 'varchar(2048)',
        'subdomains'  : 'varchar(63)',
        'languages'   : 'varchar(128)',
        'notes'       : 'text'
    }
    column_names = [
        'continent',
        'country',
        'name',
        'headquarters',
        'website',
        'subdomains',
        'languages',
        'notes'
    ]

    def __init__(self, **columns):
        super().__init__(**columns)
        if columns.get('notes'):
            self.pg_notes = columns['notes']
        else:
            self.pg_notes = 'Not available.'

    def __str__(self):
        return f'<News Source: {self.pg_newssource_name}, Country, {self.pg_newssource_country}>'
    




"""This function creates a PageModel object on the fly.
A PageModel should only be created if the content on
the page is known; therefore the function will attempt
to compile all of the <p> tags on the page prior to
instantiating the object.
"""
def create_page_models(urls: list[str], news_source: str) -> list[PageModel]:
    models = []
    for page_p_data, url in zip(compile_p_text(urls), urls):
        if not page_p_data:
            logging.error('Page does not contain any <p> data to extract. Skipping.')
            continue
        page_language = detect_string_language(page_p_data)
        page_model = PageModel(url=url, 
                            home_url=' ', p_data=page_p_data, 
                            news_source=news_source, language=page_language)
        models.append(page_model)
    return models


"""Creates a translation model in the database, which
is simply any stored written version of the article in
any language. It can be done automatically via the
googletrans module, or a human written piece of text
can be used as the translation. A translation is
"original" if it is the original translation of the
article (Original article), and is "official" if it
has been verified as accurate by a human.\n
page: PageModel (The PageModel object the translation
is to be generated from.) \n
**target_language: str (Language to translate to.) \n
auto=True: bool (Use automatic translation or not.
auto translations use google translate,) \n
text=None: str (Optional argument to use human written
text for a translation. Must not be none if auto=False.)
"""
def create_translation_model(page: PageModel, target_language=None,
                             auto=True, text=None) -> TranslationModel:
    page_uid = page['uid']
    if not target_language:
        translation_text = page['p_data']
        translation_language = page['language']
        translation_is_original = True
        translation_is_official = True
    if target_language and auto:
        translation_text = translate_page(page['p_data'], 
                                          src=page['language'],
                                          dest=target_language)
        translation_language = target_language
        translation_is_original = False
        translation_is_official = False
    elif target_language and not auto:
        if not text:
            logging.critical('Cannot create translation model without text provided! Aborting.')
            raise TranslationError("""No text was provided for the translation. To 
                                   If you do not wish to use text for the translation
                                   enable auto=True.
                                   """)
        translation_text = text
        translation_language = target_language
        translation_is_original = False
        translation_is_official = True
    translation_model = TranslationModel(
        uid=page_uid, 
        translation_text=translation_text,
        translation_language=translation_language,
        is_original=translation_is_original,
        is_official=translation_is_official,)
    return translation_model


def create_country_model(name) -> StateModel:
    geocoder = geopy.Nominatim(user_agent='allpress')
    common_name = coco.convert([name], to='name_short')
    official_name = coco.convert([name], to='name_official')
    location = geocoder.geocode(official_name)
    try:
        country_lat_long = [location.latitude, location.longitude]
    except geopy.exc.GeocoderUnavailable:
        country_lat_long = [0.0, 0.0]
        print(f'Geocoder unavailable for {official_name} ({common_name}, lat long set to (0.0,0.0).')
    except Exception:
        return StateModel(official_name='ERROR', common_name=f'{md5(urandom(10).hexdigest())}')
    print(f'Adding {official_name} ({common_name}), located at {country_lat_long}')
    return StateModel(official_name=official_name, common_name=common_name, location=country_lat_long)


def create_news_source_model(models: list) -> list:
    model_list = []
    for model in models:
        continent = model[0]
        country = model[1]
        name = model[2]
        headquarters = model[3]
        website = model[4]
        subdomains = model[5]
        languages = model[6]
        notes = model[7]
        news_source = NewsSourceModel(
            continent=continent,
            country=country,
            name=name,
            headquarters=headquarters,
            website=website,
            subdomains=subdomains,
            languages=languages,
            notes=notes,)
        model_list.append(news_source)
    return model_list
