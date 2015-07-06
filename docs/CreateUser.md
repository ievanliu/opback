
# User registration

1. decode json object containing username, email, password(text)
1. validate email and password
1. hash password with bcrypt
1. insert user into Database
1. send welcome email to user
1. send new user notification to sysadmin
1. create a session for user
1. return json response to client indicating success or failure
1. rate limit to prevent abuse or attacks
1. etc...


api as blueprint
use signals and mocks for testing
prefer decorator
custom error handler, never use abort in api endpoints
