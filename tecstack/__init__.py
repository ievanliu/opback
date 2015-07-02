
from flask import Flask
import os


# Main flask object
app = Flask(__name__)

# Config for database and log file location
app.config.from_object('config')

# init .data and .log folder in root dir
if not os.path.exists(app.config['LOGGER_FOLDER']):
    os.mkdir(app.config['LOGGER_FOLDER'])
if not os.path.exists(app.config['DB_FOLDER']):
    os.mkdir(app.config['DB_FOLDER'])

# Logging config
import logging
from logging import Formatter
from logging.handlers import RotatingFileHandler
handler = RotatingFileHandler(app.config['LOGGER_FILE'],
                              maxBytes=102400,
                              backupCount=1)
handler.setFormatter(Formatter(
    '%(asctime)s %(levelname)s: %(message)s '
    '[in %(pathname)s:%(lineno)d]'
))
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)


from flask.ext.sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)


# Authentication config
# auth = HTTPBasicAuth()

# API Registration
from flask.ext.restful import Api
api = Api(app)
