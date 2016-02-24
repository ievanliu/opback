# -*- coding:utf-8 -*-
# !/usr/bin/env python
#
# Author: Shawn.T
# Email: shawntai.ds@gmail.com
#
# This is the mgmt module of user package,
# holding user management, privilege management, and role management, etc.
#

from flask_restful import reqparse, Resource
# User Model is named Muser, to be seperated with the User API
from .models import User as Muser, Role as Mrole
from .models import user_schema, users_schema
from . import auth
from .. import app, utils


class User(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'userid', type=str, help='userid must be string')
        self.reqparse.add_argument(
            'username', type=str, help='username must be string')
        self.reqparse.add_argument(
            'password', type=str, help='password must be string')
        self.reqparse.add_argument(
            'roleid', type=str, help='roleid must be str')
        super(User, self).__init__()

    @auth.PrivilegeAuth(privilegeRequired="userAdmin")
    def get(self):
        """
        get user list or one user info
        """
        args = self.reqparse.parse_args()
        userId = args['userid']
        if not userId:
            # get the whole user list
            users = Muser.query.all()
            d = users_schema.dump(users).data
            return {'usr_infos': d}, 200
        else:
            # get one user
            user = Muser.getValidUser(userId=userId)
            if not user:
                msg = "cannot find user"
                app.logger.info(utils.logmsg(msg))
                raise utils.InvalidAPIUsage(msg)
            else:
                d = user_schema.dump(user).data
                return {'usr_infos': d}, 200

    @auth.PrivilegeAuth(privilegeRequired="userAdmin")
    def post(self):
        """
        add a new user
        """
        args = self.reqparse.parse_args()
        userName = args['username']
        hashed_password = args['password']
        roleId = args['roleid']
        # check the arguments required
        if not userName:
            msg = 'username is required'
        elif Muser.getValidUser(userName=userName):
            msg = 'username is used'
        elif len(userName) > 128:
            msg = 'userName too long'

        if not hashed_password:
            msg = 'password is requird'
        elif len(hashed_password) > 128:
            msg = 'password too long'

        if not roleId:
            msg = 'roleid is required'
        else:
            role = Mrole.getValidRole(roleId=roleId)
            if not role:
                msg = 'invalid roleid'

        if 'msg' in dir():
            app.logger.info(utils.logmsg(msg))
            raise utils.InvalidAPIUsage(msg)
        else:
            # add the new user
            user = Muser(userName=userName, hashedPassword=hashed_password,
                         role=role)
            user.insertUser()
            msg = 'user created'
            response = {"message": msg, "userid": user.user_id}
            return response, 200
