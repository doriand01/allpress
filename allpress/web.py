from copy import deepcopy
from re import match

import requests
import html.parser as parser
from bs4 import BeautifulSoup as Soup

from allpress.lexical import word
from allpress.db import models
from allpress.settings import URL_REGEX, HREF_PARSE_REGEX
from allpress import exceptions



def _html_index_helper(urlp: str, crawler) -> set:
    parser = Soup(requests.get(urlp).content, 'html.parser')
    urls_to_scan = set([url.attrs['href'] for url in list(parser.find_all('a'))])
    urls_found = set()
    for url in urls_to_scan:
        if crawler.root_url in url and url not in crawler.total_parsed:
            print(f'Appending {url} to index...')
            urls_found.add(url)
        elif crawler.root_url not in url and url not in crawler.total_parsed:
            print(f'{url} does not contain the root. Attempting to match to regex to see if it is a valid url...')
            joined_url = '/'.join([crawler.root_url, url])
            if Crawler.is_valid_url(joined_url):
                print(f'Attempting to make request to {joined_url}')
                response = requests.get(joined_url)
                if response.status_code != 200:
                    print(f'Bad response code: {response.status_code}. Skipping...')
                    continue
                else:
                    print(f'Appending {url} to index...')
    return urls_found

    

class Crawler:
    def __init__(self, root_url: str, source_name):
        self.root_url = root_url
        self.total_parsed = set()
        self.total_indexed = set()
        self.source_name = source_name

    @classmethod
    def is_valid_url(self, url: str):
        regex_match = match(URL_REGEX, url)
        if regex_match and regex_match.group() == url:
            return True
        else:
            return False 
            
    def get_root_url(self) -> str:
        return self.root_url
    
    def index_site(self, iterations=1):
        print(f'Making request to {self.root_url}...')
        response = requests.get(self.root_url)
        if response.status_code != 200:
            raise exceptions.BadWebResponseError(f'Non 200 status code: {response.status_code}')
        self.root_url = response.url
        print(f'Reponse received. Code: {response.status_code}')


        ### Index root to get primary list of urls accessible from the homepage. Will exclude all urls that redirect to pages outside of the website.
        print(f'Parsing HTML response from {self.root_url}...')
        urls_parsed = _html_index_helper(self.root_url, self)
        self.total_indexed.add(self.root_url)
        self.total_parsed = deepcopy(urls_parsed)
        iterations -= 1
        to_parse = urls_parsed
        while iterations > 0:
            print(f'Iterations remaining: {iterations}')
            new_parsed = set()
            for url in to_parse:
                if url in self.total_indexed:
                    continue
                new_parsed = new_parsed.union(_html_index_helper(url, self))
                self.total_parsed = self.total_parsed.union(new_parsed)
                self.total_indexed.add(url)
            to_parse = new_parsed - self.total_parsed
            iterations -= 1

            
       


