import sys

print(sys.path)
sys.path.append('/home/hassan2022cbtest/allpress')

import sys

print(sys.path)
sys.path.append('/home/hassan2022cbtest/allpress')
import allpress
import threading

from importlib import reload
from os import stat
from time import sleep

from allpress import web
from allpress.db import cursor
from allpress.db.models import create_page_model, create_translation_model
from allpress.exceptions import NoParagraphDataError
from allpress.lexical import statistics
from allpress import geo

coord = geo.Coordinate(0.0,0.0)
coord.move_east(2000)
coord
coord.move_west(2000)