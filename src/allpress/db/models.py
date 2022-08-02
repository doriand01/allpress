from hashlib import md5
from os import urandom

import psycopg2

from allpress.lexical import *


"""
`PageModel` is the class which models the `page` table in the Postgres database.
The page model contains columns which encapsulate the following data relating to
each indexed page: its url, the root url of the website, the `<p>` tag data
contained within the table, the language of the page, and translations for that
page.
"""
class PageModel:

    column_name_type_store = {
        'url'          : 'varchar(2048)',
        'home_url'     : 'varchar(2048)',
        'p_data'       : 'text',
        'language'     : 'varchar(3)',
        'uid'          : 'varchar(64)',
    }
    column_names = [
        'url', 'home_url',
        'p_data', 'language',
        'uid'
    ]
    def __init__(self, page_url: str, 
                 home_url: str, p_data: str, 
                 language: str):
        self.pg_page_url = encapsulate_quotes(page_url)
        self.pg_page_home_url = encapsulate_quotes(home_url)
        self.pg_page_p_data = encapsulate_quotes(p_data)
        self.pg_page_language = encapsulate_quotes(language)
        self.pg_page_translations = None
        hashobj = md5()
        hashobj.update(urandom(10))
        self.pg_page_uid = encapsulate_quotes(hashobj.hexdigest())

    def __str__(self):
        return f'<{self.pg_page_url}; {self.pg_page_language}...>'

    def __repr__(self):
        return self.__str__()

    def __getitem__(self, val):
        return getattr(self, f'pg_{self.__class__.__name__.lower().replace("model", "")}_{val}')


"""
`TranslationModel` is the class which models the `translation` table in the Postgres 
database. The translation model contains columns which encapsulate the following data 
relating to each translations in the text of each indexed page: the page's uid in the
database, the text of the translation, the language of the translation, if the
translation is the original translation of the text, and if it is an offical,
human verified translation.
"""
class TranslationModel:

    def __init__(self, page_uid: str, 
                 translation_text: str, translation_language: str, 
                 is_original: bool, is_official: bool):
        self.pg_translation_page_uid = encapsulate_quotes(page_uid)
        self.pg_translation_translation_text = encapsulate_quotes(translation_text)
        self.pg_translation_translation_language = encapsulate_quotes(translation_language)
        self.pg_translation_is_original = encapsulate_quotes(str(is_original)) ## Booleans must be converted to str
        self.pg_translation_is_official = encapsulate_quotes(str(is_official)) ## before cursor functions can be performed
                                                                               ## on them

    def __str__(self):
        return f'<Translation of {self.pg_translation_page_uid[:5]}, Lang:{self.pg_translation_translation_language}>'

    def __repr__(self):
        return self.__str__()

    def __getitem__(self, val):
        return getattr(self, f'pg_{self.__class__.__name__.lower().replace("model", "")}_{val}')


def create_page_model(url: str) -> PageModel:
    page_url = url
    page_p_data = compile_p_text(page_url)
    if not page_p_data:
        page_p_data = 'NULL'
    page_language = detect_string_language(page_p_data)
    page_model = PageModel(url, 
                           ' ', page_p_data, 
                           page_language)
    return page_model


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
        translation_text = text
        translation_language = target_language
        translation_is_original = False
        translation_is_official = True
    translation_model = TranslationModel(
        page_uid, 
        translation_text,
        translation_language,
        translation_is_original,
        translation_is_official,)
    return translation_model