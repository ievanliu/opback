
from app import db
from passlib.apps import custom_app_context as pwd_context

class Todo(db.Model):
    '''
        Todo for demo
    '''
    __tablename__ = 'todo'

    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(256))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', backref=db.backref('todos', lazy='dynamic'))

    def __init__(self, task, user):
        self.task = task
        self.user = user

    def __repr__(self):
        return '<Todo %r>' % self.id


class User(db.Model):
    '''
        User model
    '''
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True)
    email = db.Column(db.String(128))
    password_hash = db.Column(db.String(128))

    def __init__(self, username, email):
        self.username = username
        self.email = email

    def __repr__(self):
        return '<User %r>' % self.username

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)
