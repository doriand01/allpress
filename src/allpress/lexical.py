from googletrans import Translator
from bs4 import BeautifulSoup as Soup
from requests import get

def _detect_string_language(text: str) -> str:
    return Translator().translate(text).src.upper()

def _get_p_text(url: str) -> list:
    response = get(url)
    parser = Soup(response.content, 'html.parser')
    return [tag.text for tag in parser.find_all('p')]

def _compile_p_text(url: str) -> str:
    p_tags = _get_p_text(url)
    return '\n'.join(p_tags)