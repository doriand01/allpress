import csv
import json
import googletrans
import spacy

from allpress.db import models
from allpress import settings



def import_news_sources_from_file(filepath: str) -> list:
    csvfile = open(filepath, 'r', newline='')
    csv_reader = csv.reader(csvfile)
    csv_values = []
    for line in csv_reader:
        csv_values.append(line)
    return csv_values[1:]

class Indexer:

    def __init__(self, language):
        self.language = language
        self.translator = googletrans.Translator()
        self.text_processor = spacy.load('en_core_web_sm')
        self.index_in_memory = {}

    def load_index(self):
        index = json.load(open(settings.NEWS_PAGE_INDEX_FILE, 'r'))
        lang = index['languages'][self.language]
        self.index_in_memory.update(lang)


    def index_page(self, page: models.PageModel):
        processed_text = self.text_processor(page.pg_page_p_data)
        tokens = [token.lemma_ for token in processed_text if not token.is_stop and not (token.is_space or token.is_punct)]
        for token in tokens:
            if not token in self.index_in_memory.keys():
                self.index_in_memory[token] == []
                self.index_in_memory[token].append(page.pg_page_uid)
            else:
                self.index_in_memory[token].append(page.pg_page_uid)
