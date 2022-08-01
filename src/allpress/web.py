from copy import deepcopy
from re import match
from unicodedata import ucd_3_2_0
from bs4 import BeautifulSoup as Soup

from allpress import lexical
from allpress.db import models
from allpress.settings import URL_REGEX, HREF_PARSE_REGEX

import requests
import html.parser as parser





def _html_index_helper(root: str, urls_to_scan=None, prev_iteration_urls=set(), parser=None):
    if not urls_to_scan:
        parser = Soup(requests.get(root).content, 'html.parser')
        urls_to_scan = set([url.attrs['href'] for url in list(parser.find_all('a'))])
    urls_found = deepcopy(prev_iteration_urls)
    next_urls = set()
    for url in urls_to_scan:
        if root in url and url not in urls_found:
            print(f'Appending {url} to index...')
            urls_found.add(url)
            next_urls.add(url)
        elif root not in url and url not in urls_found:
            print(f'{url} does not contain the root. Attempting to match to regex to see if it is a valid url...')
            joined_url = '/'.join([root, url])
            if Crawler.is_valid_url(joined_url):
                print(f'Attempting to make request to {joined_url}')
                response = requests.get(joined_url)
                if response.status_code != 200:
                    print(f'Bad response code: {response.status_code}. Skipping...')
                    continue
                else:
                    print(f'Appending {url} to index...')
                    urls_found.add(url)
                    next_urls.add(url)
    if len(next_urls) == 0:
        return urls_found
    elif len(next_urls) > 0:
        return _html_index_helper(root, urls_to_scan=next_urls, prev_iteration_urls=urls_found, parser=parser)
    

class Crawler:
    def __init__(self, root_url: str):
        self.root_url = root_url
        self.total_indexed = set()
        self.root_index = set()

    @classmethod
    def is_valid_url(self, url: str):
        regex_match = match(URL_REGEX, url)
        if regex_match and regex_match.string == url:
            return True
        else:
            return False 

    @classmethod
    def create_page_model(self, url: str) -> models.PageModel:
        page_url = url
        page_p_data = lexical._compile_p_text(page_url)
        if not page_p_data:
            page_p_data = 'NULL'
        print(page_p_data)
        page_language = lexical._detect_string_language(page_p_data)
        page_model = models.PageModel(url, 
                                  ' ', page_p_data, 
                                  page_language)
        return page_model

    @classmethod
    def create_translation_model(self, page: models.PageModel) -> models.TranslationModel:
        page_uid = page['page_uid']
        translation_text = page['p_data']
        


    def get_root_url(self) -> str:
        return self.root_url
    
    def index_site(self):
        print(f'Making request to {self.root_url}...')
        response = requests.get(self.root_url)
        root = response.url
        print(f'Reponse received. Code: {response.status_code}')
        to_index = set()
        new_to_index = set()

        ### Index root to get primary list of urls accessible from the homepage. Will exclude all urls that redirect to pages outside of the website.
        print(f'Parsing HTML response from {root}...')
        urls_parsed = _html_index_helper(root)
        self.total_indexed = deepcopy(urls_parsed)
       


