from services import UserListApi, UserApi
from tecstack import api

api.add_resource(
    UserListApi, '/api/v0.0/users', endpoint='user_list_ep')
api.add_resource(
    UserApi, '/api/v0.0/users', endpoint='user_pep')
api.add_resource(
    UserApi, '/api/v0.0/users/<username>', endpoint='user_ep')
