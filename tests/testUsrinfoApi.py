
from nose.tools import *
import json
import os
from tecstack import app, db
from tecstack.usrinfo.services import UserListApi, UserApi
from utils import *
from tecstack.usrinfo.models import User

class TestUserApi():
    '''
        Unit test for UserListAPI and UserAPI.
    '''

    def setUp(self):
        app.testing = True
        app.config['DB_FILE'] = 'test.db'
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
                        os.path.join(app.config['DB_FOLDER'],
                        app.config['DB_FILE'])

        if not os.path.exists(app.config['DB_FOLDER']):
            os.mkdir(app.config['DB_FOLDER'])

        self.tester = app.test_client(self)
        db.create_all()
        u1 = User(
            'leannmak', '13802882778@139.com',
            '13802882778', 0)
        u1.hash_password('000000')
        u2 = User(
            'shawndai', '13802882681@139.com',
            '13802882681')
        u2.hash_password('11111111')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()

    def tearDown(self):
        db.drop_all()

    @with_setup(setUp, tearDown)
    def test_usrinfo_list_get_all(self):
        '''
        Get User list.
        '''
        # authority : 0
        args = dict(username='leannmak')
        response = self.tester.get(
            '/api/v0.0/users',
            content_type="application/json",
            data=json.dumps(args))
        eq_(response.status_code, 200)
        check_content_type(response.headers)
        u = json.loads(response.data)
        usr_infos = u['usr_infos']
        eq_(2, len(usr_infos))
        eq_('leannmak', usr_infos[0]['username'])
        # authority : 1
        args = dict(username='shawndai')
        response = self.tester.get(
            '/api/v0.0/users',
            content_type="application/json",
            data=json.dumps(args))
        eq_(response.status_code, 401)
        u = json.loads(response.data)
        eq_('Authority Failed', u['error'])

    @with_setup(setUp, tearDown)
    def test_usrinfo_get(self):
        '''
        Get a User.
        '''
        # 1. User existing
        # 1.1 Valid Password
        args = dict(password='000000')
        response = self.tester.get(
            '/api/v0.0/users/leannmak',
            content_type="application/json",
            data=json.dumps(args))
        eq_(response.status_code, 200)
        check_content_type(response.headers)
        u = json.loads(response.data)
        eq_(1, len(u))
        user = u['usr_info']
        eq_(3, len(user))
        eq_('leannmak', user['username'])
        # 1.2 Illegal Password
        args = dict(password='111111')
        response = self.tester.get(
            '/api/v0.0/users/leannmak',
            content_type="application/json",
            data=json.dumps(args))
        eq_(response.status_code, 401)
        u = json.loads(response.data)
        eq_('Password Not Match', u['error'])
        # 2. User not existing
        response = self.tester.get(
            '/api/v0.0/users/jochlam',
            content_type="application/json")
        eq_(response.status_code, 404)
        u = json.loads(response.data)
        eq_('User jochlam Not Found', u['error'])


    @with_setup(setUp, tearDown)
    def test_usrinfo_post(self):
        '''
        Post new User.
        '''
        # 1. User not existing
        args = dict(
            username='jochlam',
            email='13802882778@139.com',
            phone_number='13802882778',
            password='000111')
        response = self.tester.post(
            '/api/v0.0/users',
            content_type='application/json',
            data=json.dumps(args))
        check_content_type(response.headers)
        eq_(response.status_code, 201)
        msg = json.loads(response.data)
        eq_(2, len(msg))
        usrinfo = msg['usr_info']
        eq_(3, len(usrinfo))
        eq_('jochlam', usrinfo['username'])
        mailinfo = msg['mail_info']
        eq_(2, len(mailinfo))
        eq_('testing', mailinfo['subject']) 
        # 2. User existing
        args = dict(
            username='leannmak',
            email='13802882778@139.com',
            phone_number='13802882778',
            password='000000')
        response = self.tester.post(
            '/api/v0.0/users',
            content_type='application/json',
            data=json.dumps(args))
        eq_(response.status_code, 403)
        # 3. arguments is NULL
        args = dict(
            email='13802882778@139.com',
            phone_number='13802882778',
            password='000111')
        response = self.tester.post(
            '/api/v0.0/users',
            content_type='application/json',
            data=json.dumps(args))
        eq_(response.status_code, 404)

    @with_setup(setUp,tearDown)
    def test_usrinfo_put(self):
        '''
        Put/Update existing User.
        pay attension to the difference between dict and json string.
        {'test':'test'} vs. '{"test":"test"}'
        '''
        d = dict(phone_number='13917581195')
        # 1. User existing
        response = self.tester.put(
            '/api/v0.0/users/leannmak',
            content_type='application/json',
            data=json.dumps(d))
        check_content_type(response.headers)
        eq_(response.status_code, 201)
        u = json.loads(response.data)
        user = u['usr_info']
        eq_('leannmak', user['username'])
        eq_('13917581195', user['phone_number'])
        # 2. User not existing
        response = self.tester.put(
            '/api/v0.0/users/jochlam',
            content_type='application/json',
            data=json.dumps(d))
        eq_(response.status_code, 404)

    @with_setup(setUp,tearDown)
    def test_usrinfo_delete(self):
        '''
        Delete existing User.
        '''
        # 1. User existing
        response = self.tester.delete(
            '/api/v0.0/users/shawndai')
        eq_(response.status_code, 204)
        # 2. User not existing
        response = self.tester.delete(
            '/api/v0.0/users/jochlam')
        eq_(response.status_code, 404)
