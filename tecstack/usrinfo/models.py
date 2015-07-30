# -*- coding:utf-8 -*-

from tecstack import db, api
from passlib.apps import custom_app_context as pwd_context


class User(db.Model):

    '''
        User model
    '''
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True)
    email = db.Column(db.String(128))
    phone_number = db.Column(db.String(64))
    password_hash = db.Column(db.String(128))
    authority = db.Column(db.INT)

    def __init__(self, username, email, phone_number, authority=1):
        self.username = username
        self.email = email
        self.phone_number = phone_number
        self.authority = authority

    def __repr__(self):
        return '<User %r>' % self.username

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        valid, new_hash = pwd_context.verify_and_update(
            password,
            self.password_hash)
        if valid:
            if new_hash:
                self.password_hash = new_hash
        return valid

    @property
    def url(self):
        import services
        return api.url_for(services.UserApi, user_id=self.id)

    def to_dict(self):
        return {
            'username': self.username,
            'email': self.email,
            'phone_number': self.phone_number
        }
