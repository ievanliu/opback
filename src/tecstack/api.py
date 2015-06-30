
from flask.ext.restful import Resource, reqparse, abort
from flask import request

TODOS = {
    '1':{'task':'build a demo api'},
    '2':{'task':'build a docker container'},
    '3':{'task':'run a operation system'},
}


class TodoListApi(Resource):
    '''
        TodoList Restful API.
    '''

    def __init__(self):
        super(TodoListApi, self).__init__()
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('task', type=str)

    def get(self):
        return TODOS

    def post(self):
        args = self.parser.parse_args()
        todo_id = int(max(TODOS.keys())) + 1 # pay attention to str num cmp
        TODOS[todo_id] = {'task':args['task']}
        return TODOS[todo_id], 201


class TodoApi(Resource):
    '''
        Todo Restful API.
    '''

    def __init__(self):
        super(TodoApi, self).__init__()
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('task', type=str)

    def abort_if_todo_doesnt_exist(self, todo_id):
        if todo_id not in TODOS:
            abort(404, message="Todo {} doesn't exist".format(todo_id))

    def get(self, todo_id):
        self.abort_if_todo_doesnt_exist(todo_id)
        return TODOS[todo_id]

    def put(self, todo_id):
        self.abort_if_todo_doesnt_exist(todo_id)
        args = self.parser.parse_args()
        task = {'task': args['task']}
        TODOS[todo_id] = task
        return task, 201

    def delete(self, todo_id):
        self.abort_if_todo_doesnt_exist(todo_id)
        del TODOS[todo_id]
        return '', 204
