import sqlite3

def Model(object):
	connection = object

	def __init__(id = ''):
		self.id = id

		# INTERNALS
		# which tables we've pulled rows from
		# this should be private
		readFrom = {
			'Relationship': False,
			'Text': False,
			'Integer': False,
			'Decimal': False
		}
		pass

	def __setattribute__(self, name, value):
		print('setting ' + name)
                return object.__setattribute__(self, name, value)

        def __getattribute__(self, name):
                print('getting ' + name)
		try:
			a = object.__getattribute__(self, '_attributes')
			# throws AttributeError
		except AttributeError as noAttribute:
			#if self.readFrom[
			# read from database and hopefully that helps
			pass
                return set

	def read(self, dataType, where):
		if dataType == 'Text':
			rows = self.connection.execute('select * from Text where ')

	def save(self):
		# set createdAt or updatedAt
		pass
		

def User(Model):
	name = {
		'type': 'text'
	}
	username = {
		'type': 'text'
	}


conn = sqlite3.connect('test.db')

Model.connection = conn

