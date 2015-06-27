# all the imports
from flask_restful import reqparse, abort, Api, Resource
from db_api import app, db, User
import logging

api = Api(app)

# UserList API
class UserListAPI(Resource):
	# get the user list
	def get(self):
		query = User.query.order_by(User.id).all()
		users = [dict(username=row.username, email=row.email,password=row.password) for row in query]
		return {'users':users}
		
api.add_resource(UserListAPI, '/api/v0.0/users', endpoint = 'users')
		

# User API	
class UserAPI(Resource):
	# request parsing
	def __init__(self):
		self.reqparse = reqparse.RequestParser()
		self.reqparse.add_argument('email', type = str, help='Email cannot be converted')
		self.reqparse.add_argument('password', type = str, help='Password cannot be converted')
		super(UserAPI, self).__init__()
		
	# get a single user
	def get(self, name):
		user = User.query.filter_by(username=name).first()
		if not user:
			abort(404, message='User Not Found'.format(str))
		return {'user':user.to_json()}
		
	# add a new user
	def post(self, name):
		try:
			old_user = User.query.filter_by(username=name).first()
			if not old_user:
				args = self.reqparse.parse_args()
				new_user = User(username=name,email=args['email'],password=args['password'])
				db.session.add(new_user)
				db.session.commit()
				message = 'User %s Successfully Added' % name
				return {'message':message, 'user':new_user.to_json()}
			else:
				abort(403, message = ('User %s Already Existed' % name).format(str))
		except StandardError, e:
			logging.exception(e)
			abort(500, message = 'Server Error'.format(str))
			
	# delete a user
	def delete(self, name):
		try:
			old_user = User.query.filter_by(username=name).first()
			if old_user:
				db.session.delete(old_user)
				db.session.commit()
				message = 'User %s Successfully Deleted' % name
				return {'message':message}
			else:
				abort(404, message = 'User Not Found'.format(str))
		except StandardError, e:
			logging.exception(e)
			abort(500, message = 'Server Error'.format(str))
			
	# update a user
	def put(self, name):
		try:
			user = User.query.filter_by(username=name).first()
			if user:
				args = self.reqparse.parse_args()
				email=args['email']
				if email:
					user.email = email
				password=args['password']
				if password:
					user.password = password
				db.session.commit()
				message = 'User Info Successfully Updated'
				return {'message':message, 'user':user.to_json()}
			else:
				abort(404, message = 'User Not Found'.format(str))
		except StandardError, e:
			logging.exception(e)
			abort(500, message = 'Server Error'.format(str))
		
api.add_resource(UserAPI, '/api/v0.0/users/<string:name>', endpoint = 'user')
	
	
if __name__ == '__main__':
	app.run(debug=True)