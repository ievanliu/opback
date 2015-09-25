# -*- coding:utf-8 -*-

from tecstack import db, api
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)


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

    def generate_activate_code(self, expiration=120):
        s = Serializer(
            secret_key=api.app.config['SECRET_KEY'],
            salt=api.app.config['ACTIVATE_SALT'],
            expires_in=expiration)
        return s.dumps({'username': self.username,
                        'email': self.email,
                        'phone_number': self.phone_number,
                        'password': self.password_hash})

    @staticmethod
    def verify_activate_code(activate_code):
        s = Serializer(
            secret_key=api.app.config['SECRET_KEY'],
            salt=api.app.config['ACTIVATE_SALT'])
        try:
            data = s.loads(activate_code)
        except SignatureExpired:
            return None  # valid activate_code, but expired
        except BadSignature:
            return None  # invalid activate_code
        user = User(username=data['username'],
                    email=data['email'],
                    phone_number=data['phone_number'])
        user.password_hash = data['password']
        return user

    def generate_auth_token(self, expiration=600):
        s = Serializer(
            secret_key=api.app.config['SECRET_KEY'],
            salt=api.app.config['TOKEN_SALT'],
            expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(
            secret_key=api.app.config['SECRET_KEY'],
            salt=api.app.config['TOKEN_SALT'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None  # valid token, but expired
        except BadSignature:
            return None  # invalid token
        user = User.query.get(data['id'])
        return user

    @property
    def url(self):
        import services
        return api.url_for(services.UserApi, username=self.username)

    def to_dict(self):
        return {
            'username': self.username,
            'email': self.email,
            'phone_number': self.phone_number
        }
