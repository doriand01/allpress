import sys

print(sys.path)
sys.path.append('C:\\Users\\preit\\OneDrive\\Desktop\\coding projects\\allpress')
import allpress
import psycopg2
import pycountry

from importlib import reload
from os import stat
from time import sleep
from random import random, randint

from allpress import web
from allpress.db import cursor
from allpress.db.models import create_page_model, create_translation_model
from allpress.exceptions import NoParagraphDataError

import unittest

sources = allpress.io.import_news_sources_from_file('C:\\Users\\preit\\OneDrive\\Desktop\\coding projects\\allpress\\sources.csv')


def randomize_test_site():
    n = randint(0, len(sources))
    global crawler_default_website
    global crawler_default_source_name
    crawler_default_website = sources[n][4]
    crawler_default_source_name = sources[n][2]


class TestAllpressWebCrawler(unittest.TestCase):

    def setUp(self):
        randomize_test_site()
        self.crawler = web.Crawler(crawler_default_website, crawler_default_source_name)

    def test_crawler_init(self):
        self.assertEquals(crawler_default_source_name, self.crawler.source_name)
        self.assertEquals(crawler_default_website + '/', self.crawler.root_url)
    
    def test_crawler_get_root_url(self):
        self.assertEquals(self.crawler.get_root_url(), crawler_default_website + '/')
        self.crawler.index_site()
        self.assertEquals(self.crawler.get_root_url(), crawler_default_website + '/')
    
    def test_crawler_index_site(self):
        try:
            self.crawler.index_site()
        except Exception as e:
            self.fail(f'Test failed:{e};')

class TestAllpressWebHTMLIndexHelper(unittest.TestCase):
    
    def setUp(self):
        randomize_test_site()
        self.crawler = web.Crawler(crawler_default_website, crawler_default_source_name)

    def test_html_index_helper(self):
        self.assertIs(type(web._html_index_helper(self.crawler.get_root_url(), self.crawler)), set)

class TestAllpressGeoCoordinate(unittest.TestCase):

    def test_coordinate_init(self):
        pass

    def test_get_country_from_coordinate(self):
        latitude = random()*90
        longitude = random()*180
        if random() > 0.5: latitude *= -1
        if random() > 0.5: longitude *= -1




        

if __name__ == '__main__':
    allpress.queryall_func()
    unittest.main()

