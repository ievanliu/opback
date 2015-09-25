# -*- coding:utf-8 -*-

from flask import g, url_for
from flask.ext.mail import Message
from flask.ext.restful import reqparse, Resource, inputs
from tecstack import mail, db, ma, auth
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

    decorators = [auth.login_required]

    def __init__(self):
        super(UserListApi, self).__init__()
        self.parser = reqparse.RequestParser()

    # get user list (only open for super admin)
    @auth.login_required
    def get(self):
        if g.user.authority == 0:
            users = User.query.all()
            d = users_schema.dump(users).data
            return {'usr_infos': d}, 200
        else:
            return {'error': 'Operation Forbidden'}, 403


class UserApi(Resource):

    """
        User Api.
    """

    default_activate_code = 'helloworld'

    # send a welcome email
    @classmethod
    def send_email(cls, user, activate_code):
        with mail.record_messages() as outbox:
            msg = Message(
                subject='Welcome Mail',
                html='<p>Hello %s: </p><br/><p>Congratulations!</p><br/>Please click \
                      the link to sign in:</p><br/><p><a>%s?act=%s</a></p>'
                     % (user.username,
                        url_for('user_ep', _external=True, _scheme='https'),
                        activate_code),
                recipients=[user.email])
            mail.send(msg)
            return {'subject': outbox[0].subject}

    # 参数错误：400
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument(
            'username', type=str,
            help='username must be provided with string')
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
        self.parser.add_argument(
            'act', type=str,
            help='activate code must be provided with string',
            dest='activate_code')
        super(UserApi, self).__init__()

    # get a single User
    @auth.login_required
    def get(self, username):
        if g.user.username == username:
            return {'usr_info': g.user.to_dict()}, 200
        elif g.user.authority == 0:
            user = User.query.filter_by(username=username).first()
            return {'usr_info': user.to_dict()}, 200
        else:
            return {'error': 'Operation Forbidden'}, 403

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
        # decode json obj containing email, username, password, phone_number
        # validate username (and email) is unique
        # send a welcome and activation email to user's email
        # insert new user into database
        try:
            args = self.parser.parse_args()
            activate_code = args['activate_code']
            if activate_code == self.default_activate_code:
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
                        activate_code = user.generate_activate_code()
                        outbox = UserApi.send_email(user, activate_code)
                        return {'usr_info': user.to_dict(),
                                'activated': 'not yet',
                                'activate_code': activate_code,
                                'mail_info': outbox}, 201
                    else:
                        return {'error': 'User %s Already Existed'
                                % username}, 403
                else:
                    return {'error': 'arguments must not be NULL'}, 404
            else:
                user = User.verify_activate_code(activate_code)
                if user:
                    old_user = \
                        User.query.filter_by(username=user.username).first()
                    if not old_user:
                        db.session.add(user)
                        db.session.commit()
                    return {'usr_info': user.to_dict(),
                            'activated': 'done'}, 201
                else:
                    return {'error': 'Invalid Activate Code'}, 422
        except Exception as e:
            return {'error': e}, 500

    # delete a User
    @auth.login_required
    def delete(self, username):
        try:
            if g.user.username == username:
                db.session.delete(g.user)
                db.session.commit()
                return {}, 204
            elif g.user.authority == 0:
                old_user = User.query.filter_by(username=username).first()
                if old_user:
                    db.session.delete(old_user)
                    db.session.commit()
                    return {}, 204
                else:
                    return {'error': 'User %s Not Found' % username}, 404
            else:
                return {'error': 'Operation Forbidden'}, 403
        except Exception as e:
            return {'error': e}, 500

    # update a User
    @auth.login_required
    def put(self, username):
        try:
            if g.user.username == username:
                args = self.parser.parse_args()
                email = args['email']
                if email:
                    g.user.email = email
                phone_number = args['phone_number']
                if phone_number:
                    g.user.phone_number = phone_number
                db.session.commit()
                return {'usr_info': g.user.to_dict()}, 201
            elif g.user.authority == 0:
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
            else:
                return {'error': 'Operation Forbidden'}, 403
        except Exception as e:
            return {'error': e}, 500


class UserTokenApi(Resource):

    '''
        UserToken Restful API.
    '''

    decorators = [auth.login_required]

    def __init__(self):
        self.parser = reqparse.RequestParser()
        super(UserTokenApi, self).__init__()

    # user login
    @auth.login_required
    def get(self, username):
        if g.user.username == username:
            duration = 600
            token = g.user.generate_auth_token(duration)
            return {'token': token,
                    'duration': duration}, 200
        else:
            return {'error': 'Operation Forbidden'}, 403
