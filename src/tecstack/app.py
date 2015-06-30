# -*- coding:utf-8 -*-
#
# Author: promisejohn
# Email: promise.john@gmail.com
#


from flask import Flask, request, jsonify


# Main flask object
app = Flask(__name__)

# Config for database and log file location
app.config.from_object('config')

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
# import models so that db can find models for table generation
import models


# Authentication config
# auth = HTTPBasicAuth()

# API Registration
from flask.ext.restful import Api
api = Api(app)
from api import TodoApi, TodoListApi
api.add_resource(TodoListApi,'/demo/api/v1.0/todos')
api.add_resource(TodoApi,'/demo/api/v1.0/todos/<todo_id>')


@app.route('/')
def index():
    app.logger.info('Got visit from %s.' % request.remote_addr)
    return "Hello World!"


@app.route('/_add_numbers')
def add_numbers():
    a = request.args.get('a', 0, type=int)
    b = request.args.get('b', 0, type=int)
    return jsonify(result=a+b)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
