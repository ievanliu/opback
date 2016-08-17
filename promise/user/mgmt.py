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
from .models import User, Role
from .models import user_schema, users_schema
from . import auth
from .. import app, utils
from . import utils as userUtils


class UserAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        super(UserAPI, self).__init__()

    @auth.PrivilegeAuth(privilegeRequired="userAdmin")
    def get(self):
        """
        get user list or one user info
        """
        user = self.argCheckForGet()
        if user:
            return {'user_info': user_schema.dump(user).data}, 200
        else:
            users = User.getValidUser()
            return {'user_list': users_schema.dump(users).data}, 200

    @auth.PrivilegeAuth(privilegeRequired="userAdmin")
    def post(self):
        """
        add a new user
        """
        [user_name, password, role_list, tel, email] = self.argCheckForPost()

        # add the new user
        user = User(
            user_name=user_name, 
            hashed_password=userUtils.hash_pass(password),
            role_list=role_list,
            tel=tel,
            email=email)
        user.save()
        msg = 'user created'
        response = {"message": msg, "user_id": user.user_id}
        return response, 200

    @auth.PrivilegeAuth(privilegeRequired="userAdmin")
    def delete(self):
        """
        delete a new user
        """
        user = self.argCheckForDelete()

        # delete the new user
        user.update(valid=0)
        user.save()
        msg = 'user deleted'
        response = {"message": msg, "userid": user.user_id}
        return response, 200

    @auth.PrivilegeAuth(privilegeRequired="userAdmin")
    def put(self):
        """
        modf a user
        """
        [target_user, user_name, hashed_password, role_list, tel, email] = \
            self.argCheckForPut()
        # update user
        target_user.update(
            user_name=user_name, hashed_password=hashed_password,
            role_list=role_list, tel=tel, email=email)
        target_user.save()
        msg = 'user updated.'
        response = {"message": msg, "userid": target_user.user_id}
        return response, 200

    def argCheckForPost(self):
        self.reqparse.add_argument(
            'user_name', type=str, location='json',
            required=True, help='user name must be string')
        self.reqparse.add_argument(
            'password', type=str, location='json',
            required=True, help='password must be string')
        self.reqparse.add_argument(
            'role_name_list', type=list,  location='json',
            help='role name must be string list')
        self.reqparse.add_argument(
            'tel', type=str, location='json',
            help='tel must be str')
        self.reqparse.add_argument(
            'email', type=str, location='json',
            help='email must be str')

        args = self.reqparse.parse_args()
        user_name = args['user_name']
        password = args['password']
        tel = args['tel']
        email = args['email']

        role_name_list = args['role_name_list']
        if role_name_list:
            role_list = list()
            for role_name in role_name_list:
                role = Role.getValidRole(roleName=role_name)
                if not role:
                    msg = 'invalid role name:' + role_name
                    raise utils.InvalidAPIUsage(msg)
                role_list.append(role)
        else:
            role_list = None

        user = User.getValidUser(user_name=user_name)
        if user:
            msg = 'user name is in used.'
            raise utils.InvalidAPIUsage(msg)

        return [user_name, password, role_list, tel, email]

    def argCheckForGet(self):
        self.reqparse.add_argument(
            'user_id', type=str, location='args',
            help='user_id must be string.')

        args = self.reqparse.parse_args()
        user_id = args['user_id']
        if user_id:
            user = User.getValidUser(user_id=user_id)
            if user:
                return user
            else:
                msg = 'invalid user_id.'
                raise utils.InvalidAPIUsage(msg)
        else:
            return None

    def argCheckForDelete(self):
        self.reqparse.add_argument(
            'user_id', type=str, location='args',
            required=True, help='user_id must be string.')

        args = self.reqparse.parse_args()
        user_id = args['user_id']
        user = User.getValidUser(user_id=user_id)
        if user:
            return user
        else:
            msg = 'invalid user_id.'
            raise utils.InvalidAPIUsage(msg)

    def argCheckForPut(self):
        self.reqparse.add_argument(
            'user_id', type=str, location='args',
            required=True, help='user name must be string')
        self.reqparse.add_argument(
            'user_name', type=str, location='json',
            help='user name must be string')
        self.reqparse.add_argument(
            'password', type=str, location='json',
            help='password must be string')
        self.reqparse.add_argument(
            'role_name_list', type=list,  location='json',
            help='role name must be string list')
        self.reqparse.add_argument(
            'tel', type=str, location='json',
            help='tel must be str')
        self.reqparse.add_argument(
            'email', type=str, location='json',
            help='email must be str')

        args = self.reqparse.parse_args()
        # required args check
        user_id = args['user_id']
        target_user = User.getValidUser(user_id=user_id)
        if not target_user:
            msg = 'invalid user_id.'
            raise utils.InvalidAPIUsage(msg)

        # other args check
        role_name_list = args['role_name_list']
        if role_name_list:
            role_list = list()
            for role_name in role_name_list:
                role = Role.getValidRole(roleName=role_name)
                if not role:
                    msg = 'invalid role name:' + role_name
                    raise utils.InvalidAPIUsage(msg)
                role_list.append(role)
        else:
            role_list = None

        password = args['password']
        if password:
            hashed_password = userUtils.hash_pass(password)
        else:
            hashed_password = None

        tel = args['tel']
        email = args['email']

        user_name = args['user_name']
        if user_name:
            user = User.getValidUser(user_name=user_name)
            if user:
                msg = 'user name is in used.'
                raise utils.InvalidAPIUsage(msg)
        elif user_name is '':
            msg = 'user name should not be empty string.'
            raise utils.InvalidAPIUsage(msg)
        
        return [target_user, user_name, hashed_password, role_list, tel, email]

