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

a = statistics.calculate_named_entity_instance("""
Riyadh, Aug 11, 2022, SPA -- The Kingdom of Saudi Arabia will host - for the first time - the activities of the 22nd edition of Arab Radio & TV Festival later this year.
To be run between 7-10 November, the Festival will be organized by the Saudi Broadcasting Authority (SBA) with the participation and attendance of more than 1,000 media professionals 
from around the world, and many international media organizations, led by the World Broadcasting Unions (WBU), European Broadcasting Union (EBU), Asia-Pacific Broadcasting Union (ABU), 
African Union of Broadcasting (AUB), Asia-Pacific Institute for Broadcasting Development (AIBD), China Global Television Network (CGTN), International Telecommunication Union (ITU), and
 Mediterranean Center for Audiovisual Communication (CMCA), in addition to the participation of major media organizations from the United Kingdom, Italy and Spain, as well as the participation 
 of the Permanent Conference of the Mediterranean Audiovisual Operators (COPEAM).""")