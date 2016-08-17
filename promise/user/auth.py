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
            'user_name', type=str, help='user name must be a string')
        self.reqparse.add_argument(
            'password', type=str, help='password must be a string')
        super(UserLogin, self).__init__()

    """
    user login and return user token
    """
    def post(self):

        # check the arguments
        args = self.reqparse.parse_args()
        user_name = args['user_name']
        password = args['password']

        if not user_name:
            msg = 'you need a user_name to login.'
            app.logger.info(utils.logmsg(msg))
            raise utils.InvalidAPIUsage(msg)
        if not password:
            msg = 'you need a password to login.'
            app.logger.info(utils.logmsg(msg))
            raise utils.InvalidAPIUsage(msg)

        # try to log in
        [token, refreshToken, user, msg] = User.userLogin4token(
            user_name, password)
        if token:
            g.logined = True
            app.logger.info(utils.logmsg(msg))
            response = {"message": msg,
                        "user_name": user.user_name,
                        "token": token,
                        "rftoken": refreshToken,
                        "user_id": user.user_id,
                        "sign_up_date": user.sign_up_date,
                        "last_login": user.last_login,
                        "tel": user.tel,
                        "email": user.email}
            return response, 200
        g.logined = False
        # rewrite the msg, we do not tell them too mutch:)
        msg = 'wrong user_name & password'
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
        # if token is put in body, use this:
        # args = self.reqparse.parse_args()
        # user_name = args['token']
        if not token:
            msg = 'you need a token to login.'
            app.logger.info(utils.logmsg(msg))
            raise utils.InvalidAPIUsage(msg)
        # verify the token
        [user_id, role_id_list, msg] = User.tokenAuth(token)
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
        if not (grantType == 'refreshtoken'):
            msg = 'granttype must be "refreshtoken"'
            app.logger.info(utils.logmsg(msg))
            raise utils.InvalidAPIUsage(msg)
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
            # try:
            #     privReqId = Privilege.getFromPrivilegeName(
            #         self.privilegeRequired).privilege_id
            # except:
            #     msg = 'wrong privilege setting: privilege name(' +\
            #         self.privilegeRequired + ') not found.'
            #     app.logger.error(utils.logmsg(msg))
            #     raise utils.InvalidModuleUsage('wrong privilege setting')
            # should not use the msg here to expose the privilege name

            try:
                rolesReq = Privilege.getFromPrivilegeName(
                    self.privilegeRequired).roles
            except:
                msg = 'wrong privilege setting: privilege (' +\
                    self.privilegeRequired + ') doesnot set in any roles'
                app.logger.error(utils.logmsg(msg))
                raise utils.InvalidModuleUsage('wrong privilege setting')

            # get user's privileges by his token
            # if token is in body
            # myreqparse = reqparse.RequestParser()
            # myreqparse.add_argument('token')
            # args = myreqparse.parse_args()
            # if token is in headers
            token = request.headers.get('token')
            if not token:
                msg = "you need a token to access"
                raise utils.InvalidAPIUsage(msg)
            [user_id, roleIdList, msg] = User.tokenAuth(token)
            if not user_id:
                msg = msg + " when autherization"
                raise utils.InvalidAPIUsage(msg)
            else:
                currentUser = User.getValidUser(user_id=user_id)
                if not currentUser:
                    msg = "cannot find user when autherization"
                    raise utils.InvalidAPIUsage(msg)

            g.currentUser = currentUser

            # user's privilege auth
            for role in currentUser.roles:
                for roleReq in rolesReq:
                    if role.role_id == roleReq.role_id:
                        return fn(*args, **kwargs)
#            currentPrivileges = currentUser.role.privilege
#            if currentPrivileges:
#                privilegeAllowed = False
#                for item in currentPrivileges:
#                    if privReqId == item.privilege_id:
#                        privilegeAllowed = True
#                        break
#                if privilegeAllowed:
#                    return fn(*args, **kwargs)
            msg = "Privilege not Allowed."
            app.logger.info(utils.logmsg(msg))
            raise utils.InvalidAPIUsage(msg)
        return wrapped
