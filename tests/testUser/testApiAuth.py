# -*- coding:utf-8 -*-
# !/usr/bin/env python
#
# Author: Shawn.T
# Email: shawntai.ds@gmail.com
#
# This is the init file for the user package
# autotest for the Auth API of user package

import sys, json
sys.path.append('.')

from nose.tools import *
import json
import os

from sqlite3 import dbapi2 as sqlite3

from promise import app, db, utils
from promise.user import utils as userUtils
from promise.user.models import *
from promise.user import *

class TestApiUserLogin():
    '''
        Unit test for api: UserLigin
    '''
    # establish db
    def setUp(self):
        app.testing = True
        app.config['DB_FILE'] = 'test.db'
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
                        os.path.join(app.config['DB_FOLDER'],
                        app.config['DB_FILE'])
#        # establish log and exception handler
#        if not os.path.exists(app.config['DB_FOLDER']):
#            os.mkdir(app.config['DB_FOLDER'])
#        # Init .data and .log Folder in root dir
#        if not os.path.exists(app.config['LOGGER_FOLDER']):
#            os.mkdir(app.config['LOGGER_FOLDER'])
#        if not os.path.exists(app.config['DB_FOLDER']):
#            os.mkdir(app.config['DB_FOLDER'])
#        # init the logger obj
#        app.logger.addHandler(utils.handler)

        self.tester = app.test_client(self)
        db.create_all()

        # init privileges
        privilegeNameList = ['userAdmin', 'inventoryAdmin']
        privilegeList = []
        for item in privilegeNameList:
            newPrivilege = Privilege(item)
            db.session.add(newPrivilege)
            privilegeList.append(newPrivilege)

        # init roles
        roleRoot = Role('root')
        roleRoot.addPrivilege(privilegeList=privilegeList)
        roleOperator = Role('operator')
        roleInventoryAdmin = Role('InventoryAdmin')
        roleInventoryAdmin.addPrivilege(privilege=newPrivilege)
        db.session.add(roleRoot)
        db.session.add(roleOperator)
        db.session.add(roleInventoryAdmin)
        db.session.commit() # commit the roles before user init

        # init users
        user1 = User('tom', userUtils.hash_pass("tompass"), roleOperator)
        user2 = User('jerry', userUtils.hash_pass("jerrypass"), roleInventoryAdmin)
        rootUser = User(app.config['DEFAULT_ROOT_USER_NAME'], userUtils.hash_pass(app.config['DEFAULT_ROOT_PASSWORD']), roleRoot)
        visitor = User('visitor', 'visitor', roleOperator)

        db.session.add(rootUser)
        db.session.add(visitor)
        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()
        print 'Data imported'

        self.app = app.test_client()

    # drop db
    def tearDown(self):
        db.drop_all()

    # test to insertting data
    @with_setup(setUp, tearDown)
    def test_user_UserLogin(self):
        """
        test user login
        """
        # login with wrong username & password
        rv = self.app.post(
            '/api/v0.0/user/login', 
            data = dict(
                username = 'tom', password = 'tompass1'),
            follow_redirects = True)
        assert 'wrong username & password' in rv.data
        assert 'token' not in rv.data
        eq_(rv.status_code, 200)

        # login with correct username & password
        rv = self.app.post(
            '/api/v0.0/user/login', 
            data = dict(
                username = 'tom', password = 'tompass'),
            follow_redirects = True)
        assert 'logged in' in rv.data
        assert 'token' in rv.data
        eq_(rv.status_code, 200)


    @with_setup(setUp, tearDown)
    def test_user_tokenAuth(self):
        """
        auth test using token
        """
        # login with correct username & password
        rv = self.app.post(
            '/api/v0.0/user/login', 
            data = dict(
                username = 'tom', password = 'tompass'),
            follow_redirects = True)
        # use the token to login
        response = json.loads(rv.data)
        gotToken = response['token']
        rv = self.app.post(
            '/api/v0.0/user/tokenauth', 
            data = dict(
                token = gotToken),
            follow_redirects = True)#
        assert 'logged in' in rv.data
        eq_(rv.status_code, 200)
