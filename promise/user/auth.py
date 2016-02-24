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
from .models import User, Privilege
from .. import app, utils


class UserLogin(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'username', type=str, help='username must be a string')
        self.reqparse.add_argument(
            'password', type=str, help='password must be a string')
        super(UserLogin, self).__init__()

    """
    user login and return user token
    """
    def post(self):

        # check the arguments
        args = self.reqparse.parse_args()
        userName = args['username']
        password = args['password']

        if not userName:
            msg = 'you need a username to login.'
            app.logger.info(utils.logmsg(msg))
            raise utils.InvalidAPIUsage(msg)
        if not password:
            msg = 'you need a password to login.'
            app.logger.info(utils.logmsg(msg))
            raise utils.InvalidAPIUsage(msg)

        # try to log in
        [token, refreshToken, user, msg] = User.userLogin4token(
            userName, password)
        if token:
            g.logined = True
            app.logger.info(utils.logmsg(msg))
            response = {"message": msg,
                        "token": token,
                        "rftoken": refreshToken}
#            response.status_code = 200
            return response, 200
        g.logined = False
        # rewrite the msg, we do not tell them too mutch:)
        msg = 'wrong username & password'
        app.logger.info(utils.logmsg(msg))
        raise utils.InvalidAPIUsage(msg)


class TokenAuth(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'token', type=str, help='token must be string')
        super(TokenAuth, self).__init__()

    """
    user token authentication
    """
    def post(self):
        # check the arguments
        # if token is put in the headers, use this:
        token = request.headers.get('token')
        # if token is put in body
        # args = self.reqparse.parse_args()
        # userName = args['token']
        if not token:
            msg = 'you need a token to login.'
            app.logger.info(utils.logmsg(msg))
            raise utils.InvalidAPIUsage(msg)
        # verify the token
        [userId, roleId, msg] = User.tokenAuth(token)
        if not userId:
            app.logger.info(utils.logmsg(msg))
            raise utils.InvalidAPIUsage(msg)
        # we don't tell too much so rewrite the message
        msg = "user logged in"
        response = {"message": msg}
        return response, 200


class TokenRefresh(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'granttype', type=str, help='granttype must be "refreshtoken"')
        self.reqparse.add_argument(
            'refreshtoken', type=str, help='refreshtoken must be a string')
        super(TokenRefresh, self).__init__()

    """
    use refresh token to get a new access token
    """
    def post(self):
        # check the arguments
        args = self.reqparse.parse_args()
        grantType = args['granttype']
        rfToken = args['refreshtoken']
        if grantType is not 'refreshtoken':
            msg = 'granttype must be "refreshtoken"'
            app.logger.info(utils.logmsg(msg))
        if not rfToken:
            msg = 'you need a refreshToken to login.'
            app.logger.info(utils.logmsg(msg))
            raise utils.InvalidAPIUsage(msg)
        # get a new access token
        [token, msg] = User.tokenRefresh(rfToken)
        if not token:
            app.logger.info(utils.logmsg(msg))
            raise utils.InvalidAPIUsage(msg)

        response = {"message": msg, "token": token}
        return response, 200


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

            # check the 'privilegeRequired' argument
            try:
                privReqId = Privilege.getFromPrivilegeName(
                    self.privilegeRequired).privilege_id
            except:
                msg = 'wrong privilege setting: privilege name(' +\
                    self.privilegeRequired + ') not found.'
                app.logger.error(utils.logmsg(msg))
                raise utils.InvalidModuleUsage('wrong privilege setting')
                # should not use the msg here to expose the privilege name

            # get user's privileges by his token
            # if token is in body, use below lines
            # myreqparse = reqparse.RequestParser()
            # myreqparse.add_argument('token')
            # args = myreqparse.parse_args()
            # if token is in headers, user below line
            token = request.headers.get('token')
            if not token:
                msg = "you need a token to access"
                raise utils.InvalidAPIUsage(msg)
            [userId, roleId, msg] = User.tokenAuth(token)
            if not userId:
                msg = msg + " when autherization"
                raise utils.InvalidAPIUsage(msg)
            else:
                currentUser = User.getValidUser(userId=userId)
                if not currentUser:
                    msg = "cannot find user when autherization"
                    raise utils.InvalidAPIUsage(msg)

            # user's privilege auth
            currentPrivileges = currentUser.role.privilege
            if currentPrivileges:
                privilegeAllowed = False
                for item in currentPrivileges:
                    if privReqId == item.privilege_id:
                        privilegeAllowed = True
                        break
                if privilegeAllowed:
                    return fn(*args, **kwargs)
            msg = "Privilege not Allowed."
            app.logger.info(utils.logmsg(msg))
            raise utils.InvalidAPIUsage(msg)
        return wrapped
