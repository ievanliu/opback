# -*- coding:utf-8 -*-
# !/usr/bin/env python
#
# Author: promisejohn
# Email: promise.john@gmail.com
#
# This is the Global package of tecstack,
# holding flask app, restful api, sqlalchemy db, marshmallow ma, etc.
#

from flask import Flask
import os


# Main flask object
app = Flask(__name__)

'''
    add by Leann Mak
    2015/7/15
'''
# Config for cross domain access
from flask.ext.cors import CORS
cors = CORS(app)
'''
    end
'''

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

from flask.ext.marshmallow import Marshmallow
ma = Marshmallow(app)

# Authentication config
# auth = HTTPBasicAuth()

# API Registration
from flask.ext.restful import Api
api = Api(app)

'''
    add by Leann Mak
    2015/7/15
'''
import vminfo.services as services_vminfo
api.add_resource(
    services_vminfo.VMINFOListAPI, '/api/v0.0/vminfos', endpoint='vminfos')
api.add_resource(
    services_vminfo.VMINFOAPI, '/api/v0.0/vminfos/<string:vm_id>',
    endpoint='vminfo')
'''
    end
'''

from tecstack import auth # flake8: noqa
