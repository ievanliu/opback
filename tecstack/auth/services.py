# -*- coding:utf-8 -*-
# !/usr/bin/env python
#
# Author: promisejohn
# Email: promise.john@gmail.com
#

from flask.ext.restful import Resource, reqparse
from tecstack import db, ma
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
        args = self.parser.parse_args()
        user = User(username=args['username'], email=args['email'])

        try:
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            return {'error': e}, 500

        return UserSchema.dumps(user), 201


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
