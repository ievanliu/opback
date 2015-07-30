# -*- coding:utf-8 -*-

from flask.ext.mail import Message
from flask.ext.restful import reqparse, Resource, inputs
from tecstack import mail, db, ma
from models import User


class UserSchema(ma.HyperlinkModelSchema):

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone_number']


user_schema = UserSchema()
users_schema = UserSchema(many=True)


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
            'username', type=str,
            help='user name must be provided with string')

    def get(self):
        args = self.parser.parse_args()
        username = args['username']
        user = User.query.filter_by(username=username).first()
        if user.authority == 0:
            users = User.query.all()
            d = users_schema.dump(users).data
            return {'usr_infos': d}, 200
        else:
            return {'error': 'Authority Failed'}, 401


class UserApi(Resource):

    """
        User Api.
    """

    # send a welcome email
    @classmethod
    def send_email(cls, user):
        with mail.record_messages() as outbox:
            msg = Message(
                subject='testing',
                html='<p>Hello %s: Congratulations!<p>' % user.username,
                recipients=[user.email])
            mail.send(msg)
            return {'subject': outbox[0].subject, 'body': outbox[0].body}

    # 参数错误：400
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument(
            'username', type=str,
            help='user name must be provided with string')
        self.parser.add_argument(
            'email',
            type=inputs.regex(r'^[0-9a-zA-Z\_]{1,59}@139\.com$'),
            help='email must be provided as xxx@139.com')
        self.parser.add_argument(
            'phone_number',
            type=inputs.regex(r'^13[8|9][0-9]{8}$'),
            help='phone_number must begin with 138/139')
        self.parser.add_argument(
            'password', type=inputs.regex(r'^[0-9a-zA-Z\_]{6,16}$'),
            help='password must be longer than 6 and no longer than 16')
        super(UserApi, self).__init__()

    # get a single User (Login)
    def get(self, username):
        user = User.query.filter_by(username=username).first()
        if not user:
            return {'error': 'User %s Not Found' % username}, 404
        else:
            args = self.parser.parse_args()
            password = args['password']
            if password:
                valid = user.verify_password(password)
                if valid:
                    db.session.commit()
                    return {'usr_info': user.to_dict()}, 200
                else:
                    return {'error': 'Password Not Match'}, 401
            else:
                {'error': 'Password must not be NULL'}, 404

    # add a new User (Register)
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
        try:
            args = self.parser.parse_args()
            username = args['username']
            password = args['password']
            email = args['email']
            phone_number = args['phone_number']
            if username and password and email and phone_number:
                old_user = User.query.filter_by(username=username).first()
                if not old_user:
                    user = User(
                        username=username,
                        email=email,
                        phone_number=phone_number)
                    user.hash_password(password)
                    db.session.add(user)
                    db.session.commit()
                    outbox = UserApi.send_email(user)
                    return {'usr_info': user.to_dict(),
                            'mail_info': outbox}, 201
                else:
                    return {'error': 'User %s Already Existed' % username}, 403
            else:
                return {'error': 'arguments must not be NULL'}, 404
        except Exception as e:
            return {'error': e}, 500

    # delete a User
    def delete(self, username):
        try:
            old_user = User.query.filter_by(username=username).first()
            if old_user:
                db.session.delete(old_user)
                db.session.commit()
                return {}, 204
            else:
                return {'error': 'User %s Not Found' % username}, 404
        except Exception as e:
            return {'error': e}, 500

    # update a User
    def put(self, username):
        try:
            user = User.query.filter_by(username=username).first()
            if user:
                args = self.parser.parse_args()
                email = args['email']
                if email:
                    user.email = email
                phone_number = args['phone_number']
                if phone_number:
                    user.phone_number = phone_number
                db.session.commit()
                return {'usr_info': user.to_dict()}, 201
            else:
                return {'error': 'User %s Not Found' % username}, 404
        except Exception as e:
            return {'error': e}, 500
