import allpress
import threading

from importlib import reload
from os import stat
from sys import argv
from time import sleep

from allpress import web
from allpress.db import cursor
from allpress.db.models import create_page_model, create_translation_model
from allpress.exceptions import NoParagraphDataError
class ModuleReload(Exception):

    def __init__(self):
        super().__init__()

def stat_file(uri):
    stamp = stat(uri)
    while True:
        sleep(5)
        if stamp != stat(uri):
            raise ModuleReload
        else:
            continue
    
def reloadit():
    reload(allpress.web)
    reload(allpress.lexical)
    reload(allpress.db.models)
    reload(allpress.db.cursor)

if __name__ == '__main__':
    while True:
        thread = threading.Thread(target=stat_file, args=('/home/hassan2022cbtest/allpress/src/allpress',))
        thread.start()
        try:
            test_crawl_url = 'https://irna.ir'
            test_crawler = allpress.web.Crawler(test_crawl_url)
            test_crawler.index_site(iterations=1)
            pag_mods = []
            trans_mods = []
            for page in test_crawler.total_parsed:
                try:
                    modl= create_page_model(page)
                except NoParagraphDataError:
                    continue
                tmodl = create_translation_model(modl)
                pag_mods.append(modl)
                trans_mods.append(tmodl)  
            cursor.migrate_pages_to_db(pag_mods)   
            print('yay') 
            

        except KeyboardInterrupt:
            print('Keyboard interrupt. Hit enter to continue.')
            a = input(' ')
            print(test_crawler)
            del test_crawler
            reloadit()

        except ModuleReload:
            print('Change in module detected. Reloading...')
            del test_crawler
            reloadit()
            
        print('Tasks complete. Hit enter to reload modules and re-run.')
        a = input(' ')
        reloadit()
