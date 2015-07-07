# -*- coding:utf-8 -*-
# !/usr/bin/env python
#
# Author: promisejohn
# Email: promise.john@gmail.com
#

from flask.ext.restful import Resource, reqparse
from tecstack import ma
from tecstack.auth.models import User, Book


class UserSchema(ma.HyperlinkModelSchema):

    class Meta:
        model = User
        fields = ['id', 'username', 'books', 'url']


class BookSchema(ma.ModelSchema):

    class Meta:
        model = Book

user_schema = UserSchema()
users_schema = UserSchema(many=True)
book_schema = BookSchema()
book_schema = BookSchema(many=True)


class UserListApi(Resource):

    '''
        UserList Restful API.
    '''

    # @classmethod
    # def to_list(cls, user_list):
    #     '''
    #         TBD: try serization with marshmallow
    #     '''
    #     return [{'id': u.id, 'username': u.username, 'email': u.email}
    #             for u in user_list]

    def __init__(self):
        super(UserListApi, self).__init__()
        self.parser = reqparse.RequestParser()
        self.parser.add_argument(
            'username', type=str, help='task must be provided with string')
        self.parser.add_argument(
            'email', type=str, help='email must be provided with string')

    def get(self):
        users = User.query.all()
        d = users_schema.dump(users).data
        return d

    def post(self):
        '''
            User request a registration with email.
            System validates email(unique in sys).
            System sends an validation email to user.
            User opens url contained in the email.
            Url redirects user to complete registration with other infos.
            User created.
        '''
        # decode json obj containing email, username, password(text)
        # validate email, password
        # hash with bcrypt
        # validate username and email is unique
        # insert new user into database
        # send a welcome email to user's email


class UserApi(Resource):

    """
        User Api.
    """

    @classmethod
    def to_dict(cls, user):
        d = {'id': user.id, 'username': user.username, 'email': user.email}
        return d

    def __init__(self):
        super(UserApi, self).__init__()
        self.parser = reqparse.RequestParser()
        self.parser.add_argument(
            'username', type=str, help='task must be provided with string')
        self.parser.add_argument(
            'email', type=str, help='email must be provided with string')

    def get(self):
        pass

    def put(self):
        pass

    def delete(self):
        pass


class BookApi(Resource):

    def get(self, book_id):
        book = Book.query.get(book_id)
        return book_schema.dumps(book)
