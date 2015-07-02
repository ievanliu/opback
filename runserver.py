# -*- coding:utf-8 -*-
#
# Author: promisejohn
# Email: promise.john@gmail.com
#

from flask import request, jsonify
from tecstack import app, api
from tecstack.service import *

api.add_resource(UserListApi, '/demo/api/v1.0/users', endpoint='user_list_ep')
api.add_resource(UserApi, '/demo/api/v1.0/users/<user_id>', endpoint='user_ep')
api.add_resource(TodoListApi, '/demo/api/v1.0/todos', endpoint='todo_list_ep')
api.add_resource(TodoApi, '/demo/api/v1.0/todos/<todo_id>', endpoint='todo_ep')


@app.route('/')
def index():
    app.logger.info('Got visit from %s.' % request.remote_addr)
    return "Hello World!"


@app.route('/_add_numbers')
def add_numbers():
    a = request.args.get('a', 0, type=int)
    b = request.args.get('b', 0, type=int)
    return jsonify(result=a + b)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
