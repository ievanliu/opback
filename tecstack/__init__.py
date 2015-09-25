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

# flask mail
from flask.ext.mail import Mail
mail = Mail()

# Main flask object
app = Flask(__name__)
app.config.from_object('config')

# Config for mail
app.config.from_object('config.'+app.config['MAIL'])
mail.init_app(app)

# Config for cross domain access
from flask.ext.cors import CORS
cors = CORS(app)

app.config.from_object('config.'+app.config['SECURITY'])

# Config for database and log file location
app.config.from_object('config.'+app.config['STAGE'])

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

errors = {
    'VMIsNotFoundError': {
        'message': "A virtual machine with that id is not found.",
        'status': 404,
    },
    'VMAlreadyExistsError': {
        'message': "A virtual machine with that id already exists.",
        'status': 409,
    },
    'VMDoesNotExistError': {
        'message': "A virtual machine with that id no longer exists.",
        'status': 410,
        'extra': "Any extra information you want.",
    }
}
# API Registration
from flask.ext.restful import Api
# api = Api(app)
api = Api(app, errors=errors)

from flask.ext.httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()

from tecstack import vminfo
from tecstack import usrinfo  # flake8: noqa
from usrinfo.models import User
from flask import g

@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    user = User.verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username/password
        user = User.query.filter_by(username = username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True
