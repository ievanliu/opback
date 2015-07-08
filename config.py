import os
basedir = os.path.abspath(os.path.dirname(__file__))

DB_FOLDER = os.path.join(basedir,  '.data')
DB_FILE = 'app.db'
'''
    add by Shawn.T
'''
DB_SOURCEFILE = 'data0703.sql'
DB_FILEPATH = os.path.join(DB_FOLDER, DB_FILE)
DB_SOURCEFILEPATH = os.path.join(DB_FOLDER, DB_SOURCEFILE)

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(DB_FOLDER, DB_FILE)
LOGGER_FOLDER = os.path.join(basedir,  '.log')
LOGGER_FILE = os.path.join(LOGGER_FOLDER, 'debug.log')

