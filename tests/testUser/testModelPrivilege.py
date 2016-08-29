# -*- coding:utf-8 -*-
# !/usr/bin/env python
#
# Author: Shawn.T
# Email: shawntai.ds@gmail.com
#
# This is the init file for the user package
# autotest for the Privilege model of user package

import sys
sys.path.append('..')

from nose.tools import *
import json
import os

from sqlite3 import dbapi2 as sqlite3

from promise import app, db, utils
from promise.user import utils as userUtils
from promise.user.models import User, Privilege, Role
from tests import utils as testUtils

class TestModelsPriv():
    '''
        Unit test for model: Role
    '''
    # establish db
    def setUp(self):
        app.testing = True
        app.config['DB_FILE'] = 'test.db'
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
                        os.path.join(app.config['DB_FOLDER'],
                        app.config['DB_FILE'])
        # app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:11111111@localhost:3306/test'
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
        testUtils.importUserData()
        print 'Data imported'

   # drop db
    def tearDown(self):
        db.drop_all()

#    # test to insertting data
#    @with_setup(setUp, tearDown)
#    def test_priv_insertinfo(self):
#        '''
#        insert privilege
#        '''
#        newPriv = Privilege('newPriv')
#        newPriv.insertPrivilege()
#        gotPriv = Privilege.getValidPrivilege(privilegeName='newPriv')
#        eq_(gotPriv.privilege_name, 'newPriv')
    
    # test to deleting data
#    @with_setup(setUp)
#    def test_priv_deleteinfo(self):
#        '''
#        delete privilege
#        '''
#        userAdmin = Privilege.getValidPrivilege('userAdmin')
#        userAdmin.setInvalid()
#        role = Role.getValidRole(roleName='root')
#        eq_(role, None)#

#    # test to updating data
#    @with_setup(setUp, tearDown)
#    def test_user_updateinfo(self):
#        '''
#        update role
#        '''
#        root = Role.getValidRole(roleName='root')
#        root.role_name = 'root1'
#        db.session.commit()
#        roleGet = Role.getValidRole(roleId=root.role_id)
#        eq_(roleGet.role_name, 'root1')####

#    # test to get data
#    @with_setup(setUp, tearDown)
#    def test_role_getinfo(self):
#        '''
#        get role
#        '''
#        role = Role.getValidRole(roleName='root')
#        eq_(role.role_name, 'root')
