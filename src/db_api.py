# all the imports
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import sqlite3

# create an application
app = Flask(__name__)
app.config.from_pyfile('setting.py')

# initialize database
db = SQLAlchemy(app)
db.init_app(app)

# User Model
class User(db.Model):
	# table_name is set as __tablename__ = 'user' for class User by default, anyway you can rename them what you like
	# either SQLITE or MYSQL is ok (depends on settings.py)
	__bind_key__ = 'mysql'
	# table structure
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(20), unique=True)
	email = db.Column(db.String(50))
	password = db.Column(db.String(50))
	
	# a constructor is needed for a model
	def __init__(self, username, email, password):
		self.username = username
		self.email = email
		self.password= password
		
	def __repr__(self):
		return '<User %r>' % self.username
		
	def to_json(self):
		return {
			'username': self.username,
			'email': self.email,
			'password': self.password
			}

# connect to all kinds of databases (create tables if necessary)
db.drop_all(bind='__all__')
db.create_all(bind='__all__')
