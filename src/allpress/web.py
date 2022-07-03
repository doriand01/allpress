from copy import deepcopy
from re import match

import requests
import html.parser as parser

URL_REGEX = '((http|https)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*'

class NWSHTMLParser(parser.HTMLParser):

    urls = set()

    def crawl(self, url):
        pass

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            attr_dict = dict(attrs)
            try:
                url = attr_dict['href']
                self.urls.add(attr_dict['href'])
            except:
                print(f'Tag {tag} has no href. Skipping...')


class Crawler:

    def __init__(self, root_url):
        self.root_url = root_url
        self.total_indexed = set()
        self.root_index = set()
        self.parser = NWSHTMLParser()

    @classmethod
    def is_valid_url(self, url):
        if match(URL_REGEX, url):
            return True
        else:
            return False 
        
    def get_root_url(self):
        return self.root_url
    

    def create_url_tree(self):

        try:
            print(f'Making request to {self.root_url}...')
            response = requests.get(self.root_url)
            root = response.url
            print(f'Reponse received. Code: {response.status_code}')
            to_index = set()
            new_to_index = set()


            ### Index root to get primary list of urls accessible from the homepage. Will exclude all urls that redirect to pages outside of the website.
            print(f'Parsing HTML response from {root}...')
            self.parser.feed(response.text)
            for uri in self.parser.urls:
                if root in uri:
                    print(f'Appending {uri} to index...')
                    self.root_index.add(uri)
                    self.total_indexed.add(uri)
                else:
                    print(f'{uri} does not contain the root. Attempting to match to regex to see if it is a valid url...')
                    joined_url = '/'.join([root, uri])
                    if Crawler.is_valid_url(joined_url):
                        print(f'Attempting to make request to {joined_url}')
                        response = requests.get(joined_url)
                        if response.status_code != 200:
                            print(f'Bad response code: {response.status_code}. Skipping...')
                            continue
                        else:
                            print(f'Appending {uri} to index...')
                            self.root_index.add(uri)
                            self.total_indexed.add(uri)
            print(f'{len(self.root_index)} href urls parsed from the root url {root}.')
            to_index = self.parser.urls
            next_to_index = set()
            self.parser.urls = set()
        
            ## Parses through the touched URLs in the home page. Need to make recursive, potentially through the use of helper functions.
            while len(to_index) > 0:
                num_skipped = 0
                num_found = 0
                for href in to_index:
                    try:
                        print(f'Making request to {href}')
                        response = requests.get(href)
                        print(f'Reponse received. Code: {response.status_code}')
                        if 'html' not in response.headers['Content-Type']:
                            print(f'{href} is not an HTML page. Skipping...')
                            continue
                        self.parser.feed(response.text)
                    except Exception as e:
                        print(f'Request to {href} failed:\n {e}')
                    for uri in self.parser.urls:
                        if root not in uri:
                            num_skipped += 1
                            continue
                        elif uri not in to_index and uri not in self.total_indexed:
                            new_to_index.add(uri)
                            self.total_indexed.add(uri)
                            num_found += 1
                    self.parser.urls = set()
                print(f'LENGTH OF INDEX: {len(to_index)}')
                to_index = deepcopy(new_to_index)
                new_to_index = set()
                if num_skipped > 0:
                    print(f'{num_skipped} urls that redirected away from the website omitted from index.')
                    num_skipped = 0
                if num_found > 0:
                    print(f'{num_found} new urls found, added to index.')
                    num_found = 0
        except KeyboardInterrupt:
            print(f'Crawling interrupted. Total pages indexed: {len(self.total_indexed)}')


