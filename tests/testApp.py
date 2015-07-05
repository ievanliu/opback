# -*- coding:utf-8 -*-
#
# Author: promisejohn
# Email: promise.john@gmail.com
#

from nose.tools import with_setup, assert_equal
import json
import os


from tecstack import app, controllers


class TestApp():
    '''
    UnitTests for app.py
    '''

    def setUp(self):
        self.tester = app.test_client(self)

    def tearDown(self):
        pass

    @with_setup(setUp)
    def test_index(self):
        response = self.tester.get('/')
        assert_equal(200, response.status_code)
        assert_equal("Hello World!", response.data)

    @with_setup(setUp, tearDown)
    def test_add_numbers(self):
        '''
        test add_number, suppose success.
        '''
        response = self.tester.get(
            '/_add_numbers?a=2&b=1',
            content_type="application/json")
        assert response.status_code == 200
        assert json.loads(response.data) == {'result': 3}

    @with_setup(setUp, tearDown)
    def test_add_numbers_fail(self):
        '''
        suppose fail the test.
        '''
        response = self.tester.get(
            '/_add_numbers?a=2&b=1',
            content_type="application/json")
        assert response.status_code == 200
        assert json.loads(response.data) == {'result': 3}


if __name__ == '__main__':
    pass
