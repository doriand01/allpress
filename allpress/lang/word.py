from allpress.net import request_managers
from allpress.settings import logging

from googletrans import Translator
from lingua import LanguageDetectorBuilder, Language
from bs4 import BeautifulSoup as Soup
import iso639
import spacy

from allpress.exceptions import *

logging.getLogger(__name__)

processor = spacy.load("en_core_web_sm")
primary_language_detector = LanguageDetectorBuilder.from_all_languages().build()
fallback_language_detector = Translator().detect


def detect_string_language(text: str) -> str:
    """
    detect_string_langauge(text: str): Detects what language a given string is. \n
    Uses a primary and secondary (fallback) detector to detect languages. The \n
    primary detector uses `lingua`'s language detection capabilities. In the event \n
    that this fails, it falls back to using google translate's language detection \n
    capabilities. In the event the fallback detector fails, a not-null default value \n
    in the shape of an ISO 639 language value is returned. \n
    args; \n
    text: str \n
    \n
    returns `str`
    """
    try:
        language_iso_code = primary_language_detector.detect_language_of(text).iso_code_639_1.name
        return language_iso_code
    except Exception:
        try:
            logging.warning(f'Primary language detector failed! Using fallback language detector.')
            language_iso_code = fallback_language_detector(text).lang.upper() 
            return language_iso_code
        except Exception:
            logging.critical('Fallback language detector failed. Assigining not-null default ISO-639 value.')
            return 'und'



def compile_p_text(urls: list[str]) -> list[str]:
    """
    compile_p_text(urls: list[str]): This function compiles all of the \n
    text contained inside `<p>` tags on a web page into one single string. \n
    this function is designed to operate on URLs in batches, so it takes a \n
    list of strings containing the URLs to be compiled as an argument. The \n
    value returned is also a list of strings, each individual string containing \n
    the compiled <p> data from the URLs that were passed to the function. \n
    args; \n
    urls: list[str] (List of URLs from which the <p> data is to be compiled.) \n
    \n
    returns list[str]
    """
    manager = request_managers.HTTPRequestPoolManager()
    compiled_pages = []
    for response_future in manager.execute_request_batch(urls):
        response = response_future.result()
        if not response.request:
            logging.error('Empty bad response when compiling <p> text! Returning non-null placeholder value.')
            return ['NULLVAL']
        parser = Soup(response.content, 'html.parser')
        p_tags = '\n'.join([tag.text for tag in parser.find_all('p')])
        try:
            title = parser.find('title').text
        except Exception:
            logging.error(f"Couldn't grab title from {response.url}. Giving default title {p_tags[:25]}")
            title = p_tags[:25]
        compiled_pages.append((p_tags, title))
    return compiled_pages


def encapsulate_quotes(string: str) -> str:
    """
    encapsulate_quotes(string: str): Encapsulates text data to be inserted \n
    in the database in double dollar sign quotes. So for example, "test" becomes \n
    $$test$$. Double dollar signs are used instead of normal quotes to prevent
    quote characters in the text data from breaking the quote in the insertion \n
    Query. If the text itself contains double dollar signs, then it will break \n
    the query. This is a known bug that must be fixed. \n
    args; \n
    string: str (The string whose data is to be enclosed in dollar quotes) \n
    \n
    returns `str` \n
    """
    print(string)
    return "$$" + str(string) + "$$"


def translate_page(text: str, src: str, dest: str) -> str:
    """
    translate_page(text: str, src: str, dest: str): Translates a given string of \n
    text from a source language into a destination language. Uses the \n
    `Translator` object from the `googletrans` module. Has the same limitations \n
    in translation accuracy as google translate. \n
    args; \n
    text: str (Text of the string to be translated.)
    src: str (Source language. Should be in ISO 639 format. \n
    in other words, should be a two or three letter value that \n
    represents that language. eg. EN for 'English', ES for 'Spanish') \n
    dest: str (Destination language. Should be in ISO 639 format like \n
    `src`.)\n
    \n
    returns `str` 
    """
    translator = Translator()
    result = translator.translate(text, src=src, dest=dest).text
    return result


def remove_fragment(url: str) -> str:
    return url.split('#')[0]



def get_language_name_from_iso639(iso_code: str) -> str:
    """
    get_langauge_name_from_iso639(iso_code: str): Returns the full \n
    name for a language given its ISO 639 code. For example, passing \n
    'EN' into the function should return 'English'.
    args; \n
    iso_code: str (ISO code of the language to be converted.) \n
    \n
    returns `str`
    """
    return iso639.to_name(iso_code)

def extract_dates(text):
    processed_text = processor(text)
    dates = [date for date in processed_text.ents if date.label_ == "DATE"]
    return dates


    