import socket
myname = socket.getfqdn(socket.gethostname())
myip = socket.gethostbyname(myname)

SERVER_NAME = '%s:5000' % myip
