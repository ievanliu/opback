
from flask.ext.restful import Resource, reqparse
from tecstack import db





class TodoListApi(Resource):

    '''
        TodoList Restful API.
    '''

    @classmethod
    def to_list(cls, todo_list):
        '''
            TBD: try serization with marshmallow
        '''
        return [{'id': t.id, 'task': t.task} for t in todo_list]

    def __init__(self):
        super(TodoListApi, self).__init__()
        self.parser = reqparse.RequestParser()
        self.parser.add_argument(
            'task', type=str, help='task must be provided with string')
        self.parser.add_argument(
            'user_id', type=int, help='user_id must be provided with integer')

    def get(self):
        from models import Todo
        todos = Todo.query.all()
        d = TodoListApi.to_list(todos)
        return {'todos': d}

    def post(self):
        '''
            try webargs and WTForm(email validation) with args
        '''
        from models import Todo
        args = self.parser.parse_args()
        todo = Todo(task=args['task'])
        try:
            db.session.add(todo)
            db.session.commit()
        except Exception as e:
            return {'error': e}, 500

        return TodoApi.to_dict(todo), 201


class TodoApi(Resource):

    '''
        Todo Restful API.
    '''

    @classmethod
    def to_dict(cls, todo):
        d = {'task': todo.task, 'id': todo.id}
        return d

    def __init__(self):
        super(TodoApi, self).__init__()
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('task', type=str)

    def get(self, todo_id):
        pass

    def put(self, todo_id):
        pass  # 201

    def delete(self, todo_id):
        pass
        return {}, 204
