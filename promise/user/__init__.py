# -*- coding:utf-8 -*-
# !/usr/bin/env python
#
# Author: Shawn.T
# Email: shawntai.ds@gmail.com
#
# This is the init file for the user package
# holding api & urls of the user module
#
from .auth import TokenAPI
from .mgmt import UserAPI
from .. import api

api.add_resource(
    TokenAPI, '/api/v0.0/user/token', endpoint='token_ep')
api.add_resource(
    UserAPI, '/api/v0.0/user', endpoint='user_ep')
#api.add_resource(
#    UserLogin, '/api/v0.0/user/login', endpoint='user_login_ep')
#api.add_resource(
#    TokenAuth, '/api/v0.0/user/tokenauth', endpoint='user_tokenauth_ep')
#api.add_resource(
#    TokenRefresh, '/api/v0.0/user/tokenrefresh',
#    endpoint='user_tokenrefresh_ep')
