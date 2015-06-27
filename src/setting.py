# settings.py
	
SQLALCHEMY_DATABASE_URI = 'sqlite:////test.db'
MySQLCONF = {
		'host': 'localhost:3306',
		'user': 'root',
		'passwd': '000000',
		'db':'test',
		'charset':'utf8'
	}
SQLALCHEMY_BINDS = {
    'sqlite': 'sqlite:////test.db',
    'mysql':  'mysql+mysqlconnector://%s:%s@%s/%s?charset=%s'%(MySQLCONF['user'],MySQLCONF['passwd'],MySQLCONF['host'],MySQLCONF['db'],MySQLCONF['charset'])
}
DEBUG = True