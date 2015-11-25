# -*- coding:utf-8 -*-
# !/usr/bin/env python
#
# Author: Shawn.T
# Email: shawntai.ds@gmail.com
#
# This is the init file for the user package
# holding api & urls of the user module
#
from .auth import UserLogin, TokenAuth
from .mgmt import UserList
from .. import api

api.add_resource(
    UserList, '/api/v0.0/user/list', endpoint='user_list_ep')
api.add_resource(
    UserLogin, '/api/v0.0/user/login', endpoint='user_login_ep')
api.add_resource(
    TokenAuth, '/api/v0.0/user/tokenauth', endpoint='user_tokenauth_ep')
