
from flask.ext.restful import Resource, reqparse
from tecstack import db


class UserListApi(Resource):

    '''
        UserList Restful API.
    '''

    @classmethod
    def to_list(cls, user_list):
        '''
            TBD: try serization with marshmallow
        '''
        return [{'id': u.id, 'username': u.username, 'email': u.email}
                for u in user_list]

    def __init__(self):
        super(UserListApi, self).__init__()
        self.parser = reqparse.RequestParser()
        self.parser.add_argument(
            'username', type=str, help='task must be provided with string')
        self.parser.add_argument(
            'email', type=str, help='email must be provided with string')

    def get(self):
        from models import User
        users = User.query.all()
        d = UserListApi.to_list(users)
        return {'users': d}

    def post(self):
        from models import User
        args = self.parser.parse_args()
        user = User(username=args['username'], email=args['email'])

        try:
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            return {'error': e}, 500

        return UserApi.to_dict(user), 201


class UserApi(Resource):

    """
        User Api.
    """

    @classmethod
    def to_dict(cls, user):
        d = {'id': user.id, 'username': user.username, 'email': user.email}
        return d

    def __init__(self):
        super(UserApi, self).__init__()
        self.parser = reqparse.RequestParser()
        self.parser.add_argument(
            'username', type=str, help='task must be provided with string')
        self.parser.add_argument(
            'email', type=str, help='email must be provided with string')

    def get(self):
        pass

    def put(self):
        pass

    def delete(self):
        pass


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
