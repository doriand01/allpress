from allpress import data
from allpress import web

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))


if __name__ == '__main__':
    nws = web.create_url_tree('http://tesfanews.net')
    print('truepress')