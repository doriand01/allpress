import psycopg2

from allpress.lexical import _encapsulate_quotes
from hashlib import md5
from os import urandom

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
        self.pg_page_url = _encapsulate_quotes(page_url)
        self.pg_page_home_url = _encapsulate_quotes(home_url)
        self.pg_page_p_data = _encapsulate_quotes(p_data)
        self.pg_page_language = _encapsulate_quotes(language)
        self.pg_page_translations = None
        hashobj = md5()
        hashobj.update(urandom(10))
        self.pg_page_uid = _encapsulate_quotes(hashobj.hexdigest())

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
        self.pg_translation_page_uid = _encapsulate_quotes(page_uid)
        self.pg_translation_translation_text = _encapsulate_quotes(translation_text)
        self.pg_translation_translation_language = _encapsulate_quotes(translation_language)
        self.pg_translation_is_original = _encapsulate_quotes(is_original)
        self.pg_translation_is_official = _encapsulate_quotes(is_official)

    def __str__(self):
        return f'<Translation of {self.pg_translation_page_uid[:5]}, Lang:{self.pg_translation_translation_language}>'

    def __repr__(self):
        return self.__str__()

    def __getitem__(self, val):
        return getattr(self, f'pg_{self.__class__.__name__.lower().replace("model", "")}_{val}')