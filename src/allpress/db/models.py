from hashlib import md5
from os import urandom

import psycopg2

from allpress.lexical import *
from allpress.exceptions import TranslationError


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


"""This function creates a PageModel object on the fly.
A PageModel should only be created if the content on
the page is known; therefore the function will attempt
to compile all of the <p> tags on the page prior to
instantiating the object.
"""
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
            raise TranslationError("""No text was provided for the translation. To 
                                   If you do not wish to use text for the translation
                                   enable auto=True.
                                   """)
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