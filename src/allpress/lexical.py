from requests import get

from googletrans import Translator
from bs4 import BeautifulSoup as Soup
import iso639

from allpress.exceptions import *

"""Uses google translate to detect the language of a string."""
def detect_string_language(text: str) -> str:
    if len(text) > 5000:
        print(len(text))
        return Translator().translate(text[4999]).src.upper()
    print(len(text))
    return Translator().translate(text).src.upper()

"""Gets all of the data inside of the <p> tags of a given
webpage url. Returns as list. Helper function for `compile_p_text()`"""
def get_p_text(url: str) -> list:
    response = get(url)
    parser = Soup(response.content, 'html.parser')
    return [tag.text for tag in parser.find_all('p')]

"""Compiles all <p> data from `get_p_text()` into a single string.
"""
def compile_p_text(url: str) -> str:
    p_tags = get_p_text(url)
    joined = '\n'.join(p_tags)
    return joined


def encapsulate_quotes(string: str) -> str:
    print(string)
    return "'" + string + "'"


def translate_page(text: str, src: str, dest: str) -> str:
    translator = Translator()
    result = translator.translate(text, src=src, dest=dest).text
    return result
    