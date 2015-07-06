# -*- coding:utf-8 -*-
#!/usr/bin/env python
#
# Author: promisejohn
# Email: promise.john@gmail.com
#

from .models import User, Book
from .services import UserListApi, UserApi, BookApi
from tecstack import api

api.add_resource(
    UserListApi, '/demo/api/v1.0/users', endpoint='user_list_ep')
api.add_resource(
    UserApi, '/demo/api/v1.0/users/<user_id>', endpoint='user_ep')
api.add_resource(
    BookApi, '/demo/api/v1.0/books/<book_id>', endpoint='book_ep')
