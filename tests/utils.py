
from nose.tools import *

def check_content_type(headers):
  eq_(headers['Content-Type'], 'application/json')
