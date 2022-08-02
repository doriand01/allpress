from allpress.db import cursor
from allpress.db import models
from allpress import lexical
from allpress import web
from allpress import settings
from allpress import exceptions

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))


if __name__ == '__main__':
    nws = web.index_site('http://tesfanews.net')
    print('truepress')