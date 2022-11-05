import sys

print(sys.path)
sys.path.append('C:\\Users\\preit\\OneDrive\\Desktop\\coding projects\\allpress')
import allpress
import psycopg2
import pycountry

from importlib import reload
from os import stat
from time import sleep

from allpress import web
from allpress.db import cursor
from allpress.db.models import create_page_model, create_translation_model
from allpress.exceptions import NoParagraphDataError

import unittest

crawler_default_website = 'https://tesfanews.net'
crawler_default_source_name = 'Tesfa News'

def randomize_test_site():
    pass

def setup_crawler() -> web.Crawler:
    return web.Crawler(crawler_default_website, crawler_default_source_name)


class TestAllpressWebCrawler(unittest.TestCase):

    def test_crawler_init(self):
        crawler = setup_crawler()
        self.assertEquals(crawler_default_source_name, crawler.source_name)
        self.assertEquals(crawler_default_website, crawler.root_url)
    
    def test_crawler_get_root_url(self):
        crawler = setup_crawler()
        self.assertEquals(crawler.get_root_url(), crawler_default_website)
        crawler.index_site()
        self.assertEquals(crawler.get_root_url(), crawler_default_website)
    
    def test_crawler_index_site(self):
        crawler = setup_crawler()
        try:
            crawler.index_site()
            del crawler
            crawler = setup_crawler()
            crawler.index_site(iterations=2)
        except Exception as e:
            self.fail(f'Test failed:{e}; {e.msg} ')

class TestAllpressWebHTMLIndexHelper(unittest.TestCase):

    def test_html_index_helper(self):
        crawler = setup_crawler()
        self.assertIs(type(web._html_index_helper(crawler.get_root_url(), crawler)), set)

class TestAllpressGeoCoordinate(unittest.TestCase):

    def test_coordinate_init(self):
        pass

class TestAllpressAddAllCountriesToDB(unittest.TestCase):

    def test_add_all_countries_to_db(self):
        try:
            allpress.add_all_countries_to_db()
            cursor.db_cursor.execute('SELECT count(*) FROM pg_state;')
            num_states = cursor.fetchone()
            self.assertEqual(num_states, len(pycountry.countries))
        except:
            pass
            


        

if __name__ == '__main__':
    unittest.main()

