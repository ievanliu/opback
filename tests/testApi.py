
from nose.tools import *
import json
import os
from tecstack import app, db
from tecstack.service import TodoListApi, TodoApi, UserListApi, UserApi
from utils import *
from tecstack.models import User, Todo

class TestApi():
    '''
        Unit test for TodoListApi and TodoApi.
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
        u = User('testuser1','testuser1@tecstack.org')
        t = Todo(task='first task')
        db.session.add(u)
        db.session.add(t)
        db.session.commit()

    def tearDown(self):
        db.drop_all()

    @with_setup(setUp, tearDown)
    def test_todo_list_get(self):
        '''
        Get Todo list.
        '''
        response = self.tester.get(
            '/demo/api/v1.0/todos',
            content_type="application/json")
        eq_(response.status_code, 200)
        check_content_type(response.headers)
        d = json.loads(response.data)
        todos = d['todos']
        eq_(1, len(todos))

    @with_setup(setUp, tearDown)
    def test_todo_list_post(self):
        '''
        Post new Todo.
        '''
        d = dict(task='test todo task', user_id='1')
        response = self.tester.post(
            '/demo/api/v1.0/todos',
            content_type='application/json',
            data=json.dumps(d))

        check_content_type(response.headers)
        eq_(response.status_code, 201)
        todo = json.loads(response.data)
        eq_('test todo task', todo['task'])

    @with_setup(setUp,tearDown)
    def test_user_list_post(self):
        '''
        Post new User test.
        pay attension to the difference between dict and json string.
        {'test':'test'} vs. '{"test":"test"}'
        '''
        d = dict(username='newUser', email='new@new.com')
        response = self.tester.post(
            '/demo/api/v1.0/users',
            content_type='application/json',
            data=json.dumps(d))

        check_content_type(response.headers)
        eq_(response.status_code, 201)
        user = json.loads(response.data)
        eq_('newUser', user['username'])
