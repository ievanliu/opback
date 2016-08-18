# -*- coding:utf-8 -*-
# !/usr/bin/env python
#
# Author: Shawn.T
# Email: shawntai.ds@gmail.com
#
# This is the auth module of user package,
# using to user authutification including
# authentication(login by user&password, login by token),
# autherization(privilege auth by token, etc.)
#

from flask import g, request
from flask_restful import reqparse, Resource
from .models import User, Privilege, Role
from .. import app, utils
from . import utils as userUtils
# serializer for JWT
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
# exceptions for JWT
from itsdangerous import SignatureExpired, BadSignature, BadData
import datetime
import time

class TokenAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        super(TokenAPI, self).__init__()

    """
    user login or token refresh, return access token
    """
    def post(self):
        # check the arguments
        args = self.argCheckForPost()
        
        if args['granttype'] == 'login':
            [token, refreshToken, user, last_login, msg] = AuthMethods.login(
                args['user_name'], args['password'])
            if token:
                g.current_user = user
                app.logger.info(utils.logmsg(msg))
                response = {"message": msg,
                            "user_name": user.user_name,
                            "token": token,
                            "rftoken": refreshToken,
                            "user_id": user.user_id,
                            "sign_up_date": user.sign_up_date,
                            "last_login": last_login,
                            "tel": user.tel,
                            "email": user.email}
                return response, 200
            g.current_user = None
            # rewrite the msg, we do not tell them too mutch:)
            msg = 'wrong user_name & password'
            app.logger.info(utils.logmsg(msg))
            raise utils.InvalidAPIUsage(msg)
        elif args['granttype'] == 'refreshtoken':
            # get a new access token
            [token, msg] = AuthMethods.tokenRefresh(args['refreshtoken'])
            if not token:
                app.logger.info(utils.logmsg(msg))
                raise utils.InvalidAPIUsage(msg)
            response = {"message": msg, "token": token}
            return response, 200
        else:
            return {"message": 'wrong grant_type.'}, 500

    def argCheckForPost(self):
        self.reqparse.add_argument(
            'granttype', type=str, location='json',
            required=True, help='granttype must be "refreshtoken/login"')
        args = self.reqparse.parse_args()
        grant_type = args['granttype']
        if grant_type == 'login':
            self.reqparse.add_argument(
                'user_name', type=str, location='json',
                required=True, help='user name must be string')
            self.reqparse.add_argument(
                'password', type=str, location='json',
                required=True, help='password must be string')
            args = self.reqparse.parse_args()
            return args
        elif grant_type == 'refreshtoken':
            self.reqparse.add_argument(
                'refreshtoken', type=str, location='json',
                help='refreshtoken must be a string')
            args = self.reqparse.parse_args()
            refreshtoken = args['refreshtoken']
            return args
        else:
            raise utils.InvalidAPIUsage(
                'granttype must be "refreshtoken/login"')
    """
    user token authentication
    """
    def get(self):
        token = self.argCheckForGet()
        # verify the token
        [user_id, role_id_list, msg] = AuthMethods.tokenAuth(token)
        user = User.getValidUser(user_id = user_id)
        if not user_id:
            app.logger.info(utils.logmsg(msg))
            raise utils.InvalidAPIUsage(msg)
        else:
            user = User.getValidUser(user_id=user_id)
            if not user:
                msg = "cannot find user when autherization"
                raise utils.InvalidAPIUsage(msg)
        # we don't tell too much so rewrite the message
        msg = "user logged in"
        response = {"message": msg,
                    "user_name": user.user_name,
                    "user_id": user.user_id,
                    "sign_up_date": user.sign_up_date,
                    "tel": user.tel,
                    "email": user.email}
        return response, 200

    def argCheckForGet(self):
        self.reqparse.add_argument(
            'token', type=str, location='headers',
            required=True, help='token must be string')
        args = self.reqparse.parse_args()
        token = args['token']
        return token


class AuthMethods(Resource):
    def __init__(self, user=None):
        super(Auth, self).__init__()

    """
    user auth and return user token
    """
    @staticmethod
    def login(user_name, password):
        user = User.getValidUser(user_name=user_name)
        if not user:
            msg = 'cannot find user_name:' + user_name
            app.logger.debug(msg)
            return [None, None, None, msg]
        if not userUtils.hash_pass(password) == user.hashed_password:
            msg = 'user name and password cannot match.'
            app.logger.debug(msg)
            return [None, None, None, msg]
        # generate token sequence
        # token expiration time is set in the config file
        # the value is set in seconds: (day,second,microsecond)
        token = AuthMethods.genTokenSeq(
            user, app.config['ACCESS_TOKEN_EXPIRATION'])
        # generate refresh_token
        refreshToken = AuthMethods.genTokenSeq(
            user, app.config['REFRESH_TOKEN_EXPIRATION'])
        msg = 'user (' + user_name + ') logged in.'
        # write the login time to db
        last_login = user.last_login
        user.last_login = datetime.datetime.now()
        user.save()
        app.logger.debug(msg)
        return [token, refreshToken, user, last_login, msg]

    """
    token is generated as the JWT protocol.
    JSON Web Tokens(JWT) are an open, industry standard RFC 7519 method
    """
    @staticmethod
    def genTokenSeq(user, expires):
        s = Serializer(
            secret_key=app.config['SECRET_KEY'],
            salt=app.config['AUTH_SALT'],
            expires_in=expires)
        timestamp = time.time()
        roleIdList = []
        for role in user.roles:
            roleIdList.append(role.role_id)
        return s.dumps(
            {'user_id': user.user_id,
             'user_role': roleIdList,
             'iat': timestamp})
        # The token contains userid, user role and the token generation time.
        # u can add sth more inside, if needed.
        # 'iat' means 'issued at'. claimed in JWT.

    @staticmethod
    def tokenAuth(token):
        # token decoding
        s = Serializer(
            secret_key=app.config['SECRET_KEY'],
            salt=app.config['AUTH_SALT'])
        try:
            data = s.loads(token)
            # token decoding faild
            # if it happend a plenty of times, there might be someone
            # trying to attact your server, so it should be a warning.
        except SignatureExpired:
            msg = 'token expired'
            app.logger.warning(msg)
            return [None, None, msg]
        except BadSignature, e:
            encoded_payload = e.payload
            if encoded_payload is not None:
                try:
                    s.load_payload(encoded_payload)
                except BadData:
                    # the token is tampered.
                    msg = 'token tampered'
                    app.logger.warning(msg)
                    return [None, None, msg]
            msg = 'badSignature of token'
            app.logger.warning(msg)
            return [None, None, msg]
        except:
            msg = 'wrong token with unknown reason.'
            app.logger.warning(msg)
            return [None, None, msg]
        if ('user_id' not in data) or ('user_role' not in data):
            msg = 'illegal payload inside'
            app.logger.warning(msg)
            return [None, None, msg]
        msg = 'user(' + data['user_id'] + ') logged in by token.'
        app.logger.debug(msg)
        user_id = data['user_id']
        role_id_list = data['user_role']
        return [user_id, role_id_list, msg]

    @staticmethod
    def tokenRefresh(refreshToken):
        # varify the refreshToken
        [user_id, roleIdList, msg] = AuthMethods.tokenAuth(refreshToken)
        if user_id:
            user = User.getValidUser(user_id=user_id)
            if not user:
                msg = 'cannot find user_id'
                app.logger.warning(msg)
                return [None, msg]
        else:
            msg = 'lost user_id'
            app.logger.warning(msg)
            return [None, msg]

        if roleIdList:
            for roleId in roleIdList:
                role = Role.getValidRole(roleId=roleId)
                if not role:
                    msg = 'cannot find roleid' + roleId
                    app.logger.warning(msg)
                    return [None, msg]
        else:
            msg = 'lost roleid'
            app.logger.warning(msg)
            return [None, msg]

        token = AuthMethods.genTokenSeq(
            user, app.config['ACCESS_TOKEN_EXPIRATION'])
        msg = "token refreshed"
        return [token, msg]


class PrivilegeAuth(Resource):
    """
    This class is used tobe a decoretor for other methods to check the
    client's privilege by token.
    Your method's 'required privilege' should be set as an argument of this
    decoretor. And this 'required privilege' should have been in the
    'privilege' table.
    If your method's 'required privilege' is one of user's privileges,
    user will be allowed to access the method, otherwise not.
    ps. user's privilege is checked by his token.
    """
    def __init__(self, privilegeRequired):
        # argument 'privilegeRequired' is to set up your method's privilege
        # name
        self.privilegeRequired = privilegeRequired
        super(PrivilegeAuth, self).__init__()

    def __call__(self, fn):
        def wrapped(*args, **kwargs):

            try:
                rolesReq = Privilege.getFromPrivilegeName(
                    self.privilegeRequired).roles
            except:
                msg = 'wrong privilege setting: privilege (' +\
                    self.privilegeRequired + ') doesnot set in any roles'
                app.logger.error(utils.logmsg(msg))
                raise utils.InvalidModuleUsage('wrong privilege setting')

            token = request.headers.get('token')
            if not token:
                msg = "you need a token to access"
                raise utils.InvalidAPIUsage(msg)
            [user_id, roleIdList, msg] = AuthMethods.tokenAuth(token)
            if not user_id:
                msg = msg + " when autherization"
                raise utils.InvalidAPIUsage(msg)
            else:
                currentUser = User.getValidUser(user_id=user_id)
                if not currentUser:
                    msg = "cannot find user when autherization"
                    raise utils.InvalidAPIUsage(msg)

            g.current_user = currentUser

            # user's privilege auth
            for role in currentUser.roles:
                for roleReq in rolesReq:
                    if role.role_id == roleReq.role_id:
                        return fn(*args, **kwargs)

            msg = "Privilege not Allowed."
            app.logger.info(utils.logmsg(msg))
            raise utils.InvalidAPIUsage(msg)
        return wrapped
