# -*- coding:utf-8 -*-
#
# Author: promisejohn
# Email: promise.john@gmail.com
#


from flask import Flask, request, jsonify
import logging
from logging import Formatter
from logging.handlers import RotatingFileHandler
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///%s/../.data/sqlite3.db' \
                                            % app.instance_path
app.config['LOGGER_FILE'] = '.log/debug.log'

db = SQLAlchemy(app)
# auth = HTTPBasicAuth()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    password_hash = db.Column(db.String(128))

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)


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
    handler = RotatingFileHandler(app.config['LOGGER_FILE'], maxBytes=102400, backupCount=1)
    handler.setFormatter(Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]'
    ))
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)

    db.drop_all()
    db.create_all()

    app.run(host='0.0.0.0', port=5000, debug=True)
