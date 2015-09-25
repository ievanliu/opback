
from nose.tools import *
import base64
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
        u3 = User(
            'headkarl', '13802880354@139.com',
            '13802880354')
        u3.hash_password('000000')
        db.session.add(u1)
        db.session.add(u2)
        db.session.add(u3)
        db.session.commit()

    def tearDown(self):
        db.drop_all()

    @with_setup(setUp, tearDown)
    def test_usrinfo_list_get_all(self):
        '''
        Get User list.
        '''
        # 1. authority fail
        base64string = base64.encodestring('%s:%s' % ('shawndai', '11110000'))[:-1]
        headers=[("Authorization", "Basic %s" % base64string)]
        args = dict(username='shawndai')
        response = self.tester.get(
            '/api/v0.0/users',
            headers=headers,
            content_type="application/json",
            data=json.dumps(args))
        eq_(response.data, 'Unauthorized Access')
        # 2. authority : 0
        args = dict(username='leannmak')
        base64string = base64.encodestring('%s:%s' % ('leannmak', '000000'))[:-1]
        headers=[("Authorization", "Basic %s" % base64string)]
        response = self.tester.get(
            '/api/v0.0/users',
            headers=headers,
            content_type="application/json",
            data=json.dumps(args))
        eq_(response.status_code, 200)
        check_content_type(response.headers)
        u = json.loads(response.data)
        usr_infos = u['usr_infos']
        eq_(3, len(usr_infos))
        eq_('leannmak', usr_infos[0]['username'])
        # 3. authority : 1
        base64string = base64.encodestring('%s:%s' % ('shawndai', '11111111'))[:-1]
        headers=[("Authorization", "Basic %s" % base64string)]
        args = dict(username='shawndai')
        response = self.tester.get(
            '/api/v0.0/users',
            headers=headers,
            content_type="application/json",
            data=json.dumps(args))
        eq_(response.status_code, 403)
        u = json.loads(response.data)
        eq_('Operation Forbidden', u['error'])

    @with_setup(setUp, tearDown)
    def test_usrinfo_get(self):
        '''
        Get a User.
        '''
        # 1. authority fail
        base64string = base64.encodestring('%s:%s' % ('shawndai', '11110000'))[:-1]
        headers=[("Authorization", "Basic %s" % base64string)]
        response = self.tester.get(
            '/api/v0.0/users/shawndai',
            headers=headers,
            content_type="application/json")
        eq_(response.data, 'Unauthorized Access')
        # 2. authority : 0
        base64string = base64.encodestring('%s:%s' % ('leannmak', '000000'))[:-1]
        headers=[("Authorization", "Basic %s" % base64string)]
        response = self.tester.get(
            '/api/v0.0/users/shawndai',
            headers=headers,
            content_type="application/json")
        eq_(response.status_code, 200)
        check_content_type(response.headers)
        u = json.loads(response.data)
        eq_(1, len(u))
        user = u['usr_info']
        eq_(3, len(user))
        eq_('shawndai', user['username'])
        # 3. authority : 1
        base64string = base64.encodestring('%s:%s' % ('shawndai', '11111111'))[:-1]
        headers=[("Authorization", "Basic %s" % base64string)]
        # 3.1 check own
        response = self.tester.get(
            '/api/v0.0/users/shawndai',
            headers=headers,
            content_type="application/json")
        eq_(response.status_code, 200)
        check_content_type(response.headers)
        u = json.loads(response.data)
        eq_(1, len(u))
        user = u['usr_info']
        eq_(3, len(user))
        eq_('shawndai', user['username'])
        # 3.2 check others
        response = self.tester.get(
            '/api/v0.0/users/leannmak',
            headers=headers,
            content_type="application/json")
        eq_(response.status_code, 403)
        u = json.loads(response.data)
        eq_('Operation Forbidden', u['error'])

    @with_setup(setUp, tearDown)
    def test_usrinfo_post(self):
        '''
        Post new User.
        for user sign-up.
        '''
        # not yet activated 
        # 1. user not existing
        args = dict(
            username='jochlam',
            email='13802882778@139.com',
            phone_number='13802882778',
            password='000111',
            act='helloworld')
        response = self.tester.post(
            '/api/v0.0/users',
            content_type='application/json',
            data=json.dumps(args))
        check_content_type(response.headers)
        eq_(response.status_code, 201)
        msg = json.loads(response.data)
        eq_(4, len(msg))
        usrinfo = msg['usr_info']
        eq_(3, len(usrinfo))
        eq_('jochlam', usrinfo['username'])
        mailinfo = msg['mail_info']
        eq_(1, len(mailinfo))
        eq_('Welcome Mail', mailinfo['subject'])
        eq_('not yet', msg['activated']) 
        # 2. user existing
        args = dict(
            username='leannmak',
            email='13802882778@139.com',
            phone_number='13802882778',
            password='000000',
            act='helloworld')
        response = self.tester.post(
            '/api/v0.0/users',
            content_type='application/json',
            data=json.dumps(args))
        eq_(response.status_code, 403)
        # 3. arguments is NULL
        args = dict(
            email='13802882778@139.com',
            phone_number='13802882778',
            password='000111',
            act='helloworld')
        response = self.tester.post(
            '/api/v0.0/users',
            content_type='application/json',
            data=json.dumps(args))
        eq_(response.status_code, 404)
        # activated ok
        args = dict(act=msg['activate_code'])
        response = self.tester.post(
            '/api/v0.0/users',
            content_type='application/json',
            data=json.dumps(args))
        eq_(response.status_code, 201)
        msg = json.loads(response.data)
        eq_(2, len(msg))
        usrinfo = msg['usr_info']
        eq_(3, len(usrinfo))
        eq_('jochlam', usrinfo['username'])
        eq_('done', msg['activated']) 

    @with_setup(setUp,tearDown)
    def test_usrinfo_put(self):
        '''
        Put/Update existing User.
        pay attension to the difference between dict and json string.
        {'test':'test'} vs. '{"test":"test"}'
        '''
        # 1. authority fail
        base64string = base64.encodestring('%s:%s' % ('shawndai', '11110000'))[:-1]
        headers=[("Authorization", "Basic %s" % base64string)]
        d = dict(phone_number='13917581195')
        response = self.tester.put(
            '/api/v0.0/users/shawndai',
            headers=headers,
            content_type="application/json",
            data=json.dumps(d))
        eq_(response.data, 'Unauthorized Access')
        # 2. authority : 0
        base64string = base64.encodestring('%s:%s' % ('leannmak', '000000'))[:-1]
        headers=[("Authorization", "Basic %s" % base64string)]
        d = dict(phone_number='13917581195')
        # 2.1 user existing
        response = self.tester.put(
            '/api/v0.0/users/shawndai',
            headers=headers,
            content_type="application/json",
            data=json.dumps(d))
        check_content_type(response.headers)
        eq_(response.status_code, 201)
        u = json.loads(response.data)
        user = u['usr_info']
        eq_('shawndai', user['username'])
        eq_('13917581195', user['phone_number'])
        # 2.2 user not existing
        response = self.tester.put(
            '/api/v0.0/users/jochlam',
            headers=headers,
            content_type='application/json',
            data=json.dumps(d))
        eq_(response.status_code, 404)
        # 3. authority : 1
        base64string = base64.encodestring('%s:%s' % ('shawndai', '11111111'))[:-1]
        headers=[("Authorization", "Basic %s" % base64string)]
        # 3.1 update own
        d = dict(phone_number='13802882689')
        response = self.tester.put(
            '/api/v0.0/users/shawndai',
            headers=headers,
            content_type="application/json",
            data=json.dumps(d))
        check_content_type(response.headers)
        eq_(response.status_code, 201)
        u = json.loads(response.data)
        user = u['usr_info']
        eq_('shawndai', user['username'])
        eq_('13802882689', user['phone_number'])
        # 3.2 update others
        response = self.tester.put(
            '/api/v0.0/users/headkarl',
            headers=headers,
            content_type="application/json",
            data=json.dumps(d))
        eq_(response.status_code, 403)
        u = json.loads(response.data)
        eq_('Operation Forbidden', u['error'])

    @with_setup(setUp,tearDown)
    def test_usrinfo_delete(self):
        '''
        Delete existing User.
        '''
        # 1. authority fail
        base64string = base64.encodestring('%s:%s' % ('shawndai', '11110000'))[:-1]
        headers=[("Authorization", "Basic %s" % base64string)]
        response = self.tester.delete(
            '/api/v0.0/users/shawndai',
            headers=headers)
        eq_(response.data, 'Unauthorized Access')
        # 2. authority : 0
        base64string = base64.encodestring('%s:%s' % ('leannmak', '000000'))[:-1]
        headers = [("Authorization", "Basic %s" % base64string)]
        # 2.1 user existing
        response = self.tester.delete(
            '/api/v0.0/users/shawndai',
            headers=headers)
        eq_(response.status_code, 204)
        # 2.2 user not existing
        response = self.tester.delete(
            '/api/v0.0/users/jochlam',
            headers=headers)
        eq_(response.status_code, 404)
        # 3. authority : 1
        base64string = base64.encodestring('%s:%s' % ('headkarl', '000000'))[:-1]
        headers=[("Authorization", "Basic %s" % base64string)]
        # 3.1 delete others
        response = self.tester.delete(
            '/api/v0.0/users/leannmak',
            headers=headers)
        eq_(response.status_code, 403)
        u = json.loads(response.data)
        eq_('Operation Forbidden', u['error'])
        # 3.2 delete own
        response = self.tester.delete(
            '/api/v0.0/users/headkarl',
            headers=headers)
        eq_(response.status_code, 204)

    @with_setup(setUp, tearDown)
    def test_token_get(self):
        '''
        Get a User Token.
        for user sign-in.
        '''
        # 1. authority fail
        base64string = base64.encodestring('%s:%s' % ('shawndai', '11110000'))[:-1]
        headers = [("Authorization", "Basic %s" % base64string)]
        response = self.tester.get(
            '/api/v0.0/tokens/shawndai',
            headers=headers,
            content_type="application/json")
        eq_(response.data, 'Unauthorized Access')
        # 2. get one own
        base64string = base64.encodestring('%s:%s' % ('leannmak', '000000'))[:-1]
        headers = [("Authorization", "Basic %s" % base64string)]
        response = self.tester.get(
            '/api/v0.0/tokens/leannmak',
            headers=headers,
            content_type="application/json")
        eq_(response.status_code, 200)
        check_content_type(response.headers)
        u = json.loads(response.data)
        eq_(2, len(u))
        eq_(600, u['duration'])
        # 3. get others
        response = self.tester.get(
            '/api/v0.0/tokens/shawndai',
            headers=headers,
            content_type="application/json")
        eq_(response.status_code, 403)
        u = json.loads(response.data)
        eq_('Operation Forbidden', u['error'])

    @with_setup(setUp, tearDown)
    def test_token_validity(self):
        '''
        Test a User Token.
        '''
        # 1. login: get one's token
        base64string = base64.encodestring('%s:%s' % ('leannmak', '000000'))[:-1]
        headers = [("Authorization", "Basic %s" % base64string)]
        response = self.tester.get(
            '/api/v0.0/tokens/leannmak',
            headers=headers,
            content_type="application/json")
        eq_(response.status_code, 200)
        check_content_type(response.headers)
        u = json.loads(response.data)
        eq_(2, len(u))
        eq_(600, u['duration'])
        # 2. operation: get one's info
        base64string = base64.encodestring('%s:' % u['token'])[:-1]
        headers = [("Authorization", "Basic %s" % base64string)]
        response = self.tester.get(
            '/api/v0.0/users/leannmak',
            headers=headers,
            content_type="application/json")
        eq_(response.status_code, 200)
        check_content_type(response.headers)
        u = json.loads(response.data)
        eq_(1, len(u))
        user = u['usr_info']
        eq_(3, len(user))
        eq_('leannmak', user['username'])
        # 3. operation: update one's info
        d = dict(phone_number='13802882689')
        response = self.tester.put(
            '/api/v0.0/users/leannmak',
            headers=headers,
            content_type="application/json",
            data=json.dumps(d))
        check_content_type(response.headers)
        eq_(response.status_code, 201)
        u = json.loads(response.data)
        user = u['usr_info']
        eq_('leannmak', user['username'])
        eq_('13802882689', user['phone_number'])
        # 4. operation: delete a user
        response = self.tester.delete(
            '/api/v0.0/users/leannmak',
            headers=headers)
        eq_(response.status_code, 204)
