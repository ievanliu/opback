# -*- coding:utf-8 -*-
# !/usr/bin/env python
#
# Author: Leann Mak
# Email: leannmak@139.com
# Date: Apr 16, 2016
#
# This is autotest for Host API of cmdb package.

import sys, json
sys.path.append('.')

from nose.tools import *
import os

from sqlite3 import dbapi2 as sqlite3

from promise import app, db, utils
from promise.user import utils as userUtils
from promise.user.models import *


class TestHostAPI():
    '''
        Unit test for API: Host/HostList
    '''
    # log in
    def setUp(self):
        app.testing = True
        app.config['DB_FILE'] = 'test.db'
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
            os.path.join(app.config['DB_FOLDER'], app.config['DB_FILE'])

        self.tester = app.test_client(self)

        # 1. db init: import user info
        db.create_all()
        # 1.1 init privileges
        privilegeNameList = ['userAdmin', 'inventoryAdmin']
        privilegeList = []
        for item in privilegeNameList:
            newPrivilege = Privilege(item)
            db.session.add(newPrivilege)
            privilegeList.append(newPrivilege)
        # 1.2 init roles: should be committed before user init
        roleRoot = Role('root')
        roleRoot.addPrivilege(privilegeList=privilegeList)
        db.session.commit()
        # 1.3 init users
        rootUser = User(
            app.config['DEFAULT_ROOT_USER_NAME'],
            userUtils.hash_pass(app.config['DEFAULT_ROOT_PASSWORD']),
            roleRoot)
        db.session.add(rootUser)
        db.session.commit()

        # 2. user login: get user token
        login = self.tester.post(
            '/api/v0.0/user/login',
            data=dict(
                username=app.config['DEFAULT_ROOT_USER_NAME'],
                password=app.config['DEFAULT_ROOT_PASSWORD']))
        self.token = json.loads(login.data)['token']

    # log out
    def tearDown(self):
        self.token = ''
        db.drop_all()

    @with_setup(setUp, tearDown)
    def test_host_api_all(self):
        """
            get host(s) existing
        """
        # 1. get host list
        # 1.1 no paging
        response = self.tester.get(
            '/api/v0.0/host',
            headers={'token': self.token})
        assert 'data' in response.data
        eq_(response.status_code, 200)
        data = json.loads(response.data)['data']
        # 1.2 paging
        # 1.2.1 use default per page
        d = dict(page=1)
        response = self.tester.get(
            '/api/v0.0/host',
            headers={'token': self.token},
            content_type='application/json',
            data=json.dumps(d))
        assert 'data' in response.data
        assert 'totalpage' in response.data
        eq_(response.status_code, 200)
        # 1.2.2 use custom per page
        d = dict(page=1, pp=1)
        response = self.tester.get(
            '/api/v0.0/host',
            headers={'token': self.token},
            content_type='application/json',
            data=json.dumps(d))
        assert 'data' in response.data
        assert 'totalpage' in response.data
        eq_(response.status_code, 200)

        # 2. get a host
        # 2.1 host found (if hostlist not null)
        if data:
            host = data[0]
            assert 'hostid' in host
            hostid = host['hostid']
            response = self.tester.get(
                '/api/v0.0/host/%s' % hostid,
                headers={'token': self.token})
            assert 'data' in response.data
            eq_(response.status_code, 200)
            data = json.loads(response.data)['data']
            assert 'interfaces' in data
            assert 'groups' in data
            assert 'inventory' in data
        # 2.2 host not found
        response = self.tester.get(
            '/api/v0.0/host/iamahost4test',
            headers={'token': self.token})
        assert 'error' in response.data
        error = json.loads(response.data)['error']
        assert 'Host Not Found' in error
        eq_(response.status_code, 404)
