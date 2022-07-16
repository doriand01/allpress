import psycopg2

class PageModel:

    def __init__(self, page_url: str, parent_page: str, p_data: tuple, language: str, translations: list):
        self.pg_page_url = page_url
        self.pg_page_parent_page = parent_page
        self.pg_page_p_data = p_data
        self.pg_page_language = language
        self.pg_page_translations = translations