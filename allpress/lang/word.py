from allpress.net import request_managers
from allpress.settings import logging

from googletrans import Translator
from lingua import LanguageDetectorBuilder, Language
from bs4 import BeautifulSoup as Soup
import iso639

from allpress.exceptions import *

logging.getLogger(__name__)

primary_language_detector = LanguageDetectorBuilder.from_all_languages().build()
fallback_language_detector = Translator().detect

"""Uses google translate to detect the language of a string."""
def detect_string_language(text: str) -> str:
    try:
        language_iso_code = primary_language_detector.detect_language_of(text).iso_code_639_1.name
        return language_iso_code
    except Exception:
        try:
            logging.warning(f'Primary language detector failed! Using fallback language detector.')
            language_iso_code = fallback_language_detector(text).lang.upper() 
            return language_iso_code
        except Exception:
            logging.critical('Fallback language detector failed. Assigining not-null default value.')
            return 'XX'


"""Compiles all <p> data from the url into a single string.
"""
def compile_p_text(urls: list) -> list[str]:
    manager = request_managers.HTTPRequestPoolManager()
    compiled_pages = []
    for response_future in manager.execute_request_batch(urls):
        response = response_future.result()
        if not response.request:
            logging.error('Empty bad response when compiling <p> text! Returning non-null placeholder value.')
            return ['NULLVAL']
        parser = Soup(response.content, 'html.parser')
        p_tags = [tag.text for tag in parser.find_all('p')]
        compiled_pages.append('\n'.join(p_tags))
    return compiled_pages

"""Encapsulates string data in SQL-type quotation marks,
in order to reduce chance of syntax errors in database values. 
"""
def encapsulate_quotes(string: str) -> str:
    print(string)
    return "$$" + str(string) + "$$"


def translate_page(text: str, src: str, dest: str) -> str:
    translator = Translator()
    result = translator.translate(text, src=src, dest=dest).text
    return result


def remove_fragment(url: str) -> str:
    return url.split('#')[0]

def get_language_name_from_iso639(iso_code: str) -> str:
    return iso639.to_name(iso_code)
    