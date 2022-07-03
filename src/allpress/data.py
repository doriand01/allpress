

class URLTree:

    @classmethod
    def crawl(url):
        pass

    def __init__(self):
        pass


class NewsWebsite:

    def __init__(self, home_url):
        self.root_url = home_url
        self.home_page_response = requests.get(self.home_url)
