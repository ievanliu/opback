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
from .models import User, users_schema
from . import auth


class UserList(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'token', type=str, help='token must be string')
        super(UserList, self).__init__()

    @auth.PrivilegeAuth(privilegeRequired="userAdmin")
    def get(self):
        users = User.query.all()
        d = users_schema.dump(users).data
        return {'usr_infos': d}, 200
