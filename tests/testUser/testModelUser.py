# -*- coding:utf-8 -*-
# !/usr/bin/env python
#
# Author: Shawn.T
# Email: shawntai.ds@gmail.com
#
# This is the init file for the user package
# autotest for the Privilege model of user package

import sys
sys.path.append('.')

from nose.tools import *
import json
import os

from sqlite3 import dbapi2 as sqlite3

from promise import app, db, utils
from promise.user import utils as userUtils
from promise.user.models import User, Privilege, Role

class TestModelsUser():
    '''
        Unit test for model: User
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

    # drop db
    def tearDown(self):
        db.drop_all()

    # test to insertting data
    @with_setup(setUp, tearDown)
    def test_role_insertinfo(self):
        '''
        insert user
        '''
        roleOperator = Role.getValidRole(roleName='operator')
        mike = User('mike', userUtils.hash_pass("mikepass"), roleOperator)
        mikeUserId = mike.user_id
        mike.insertUser()
        user = User.getValidUser(userId=mikeUserId)
        eq_(user.user_name, 'mike')
    
    # test to deleting data
    @with_setup(setUp, tearDown)
    def test_user_deleteinfo(self):
        '''
        delete user
        '''
        tom = User.getValidUser(userName='tom')
        tom.setInvalid()
        searchUser = User.getValidUser(userName='tom')
        eq_(searchUser, None)#

    # test to updating data
    @with_setup(setUp, tearDown)
    def test_user_updateinfo(self):
        '''
        update user
        '''
        user = User.getValidUser(userName='tom')
        user.hashed_password = userUtils.hash_pass('tompass1')
        User.updateUser(user)
        user_get = User.getValidUser(userName='tom')
        eq_(user_get.hashed_password, userUtils.hash_pass('tompass1'))#

    # test to get data
    @with_setup(setUp, tearDown)
    def test_user_getinfo(self):
        '''
        get user & get Relate role
        '''
        user = User.getValidUser(userName='tom')
        eqTag = 0
        roles = user.roles
        for role in roles:
            if role.role_name == 'operator':
                eqTag = 1
        eq_(eqTag, 1)

    # test userLogin4Token
    @with_setup(setUp, tearDown)
    def test_user_Login4token(self):
        testUser = User.getValidUser(userName='tom')
        [token, refreshToken, user, msg] = User.userLogin4token('tom','tompass')
        eq_(user.user_id, testUser.user_id)


