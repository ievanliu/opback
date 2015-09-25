from services import UserListApi, UserApi, UserTokenApi
from tecstack import api

api.add_resource(
    UserListApi, '/api/v0.0/users', endpoint='user_list_ep')
api.add_resource(
    UserApi, '/api/v0.0/users', endpoint='user_ep')
api.add_resource(
    UserApi, '/api/v0.0/users/<username>', endpoint='user_name_ep')
api.add_resource(
    UserTokenApi, '/api/v0.0/tokens/<username>', endpoint='user_token_ep')
