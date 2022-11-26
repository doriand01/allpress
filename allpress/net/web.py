from copy import deepcopy
from re import match

import html.parser as parser

from bs4 import BeautifulSoup as Soup

from allpress.lang import word
from allpress.net import request_managers
from allpress.db import models
from allpress.settings import URL_REGEX, WEB_CRAWLER_OUTPUT_FOLDER, logging
from allpress import exceptions

logging.getLogger(__name__)

def _html_index_helper(urls: list, crawler) -> set:
    urls_found = set()
    manager = request_managers.HTTPRequestPoolManager()
    for response_future in manager.execute_request_batch(urls):
        response = response_future.result()
        if not response.request:
            logging.warning('Empty response object! Skipping scraping for this page.')
            continue
        parser = Soup(response.content, 'html.parser')
        urls_to_scan = set([url.attrs['href'] for url in list(parser.find_all('a')) if 'href' in url.attrs.keys()])
        for url in urls_to_scan:
            if crawler.root_url in url and url not in crawler.total_parsed:
                # `Adds URLs found from page being scanned to the set of discovered URLs,
                # if they are not already in the Crawler object's stored list of previously
                # discovered URLs.
                urls_found.add(url)
                logging.info(f'Adding url {url} to the index.')
            elif crawler.core_url not in url and url not in crawler.total_parsed:
                logging.info(f'{url} does not contain the root. Attempting to match to regex to see if it is a valid url...')
                joined_url = f'{crawler.root_url}/{url}'
                if Crawler.is_valid_url(joined_url):
                    logging.info(f'{joined_url} matches with verification regex. Adding to the index.')
                    urls_found.add(joined_url)
                elif url.startswith('//') and Crawler.is_valid_url(url[2:]) and crawler.core_url in url:
                    logging.info(f'{url[2:]} matches with verification regex. Adding to the index.')
                    urls_found.add(url[2:])
    
    
    
    return urls_found

    
class Crawler:

    def __init__(self, root_url: str, source_name):
        self.root_url = root_url
        self.core_url = match(URL_REGEX, root_url).groups()[2]
        self.total_parsed = set()
        self.to_scan = set()
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
        to_parse = [self.root_url]
        ### Index root to get primary list of urls accessible from the homepage. Will exclude all urls that redirect to pages outside of the website.
        while iterations > 0:
            new_parsed = set()
            new_parsed = new_parsed.union(_html_index_helper(list(to_parse), self))
            self.total_parsed = self.total_parsed.union(new_parsed)
            self.total_indexed = self.total_indexed.union(set(to_parse))
            to_parse = new_parsed - set(to_parse)
            iterations -= 1


    def output_scraped_urls(self):
        output_file = open(f'{WEB_CRAWLER_OUTPUT_FOLDER}\\{self.source_name.lower().replace(" ", "")}.txt', 'a')
        for url in self.total_parsed:
            output_file.write(f'{url}\n')
        output_file.close()


       


