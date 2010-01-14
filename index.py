#import sqlite3

class Model:
	id = {
		'type': 'text'
	}
	#connection = object
	def __init__(self, id = None):
		self.id = id

		# INTERNALS
		# which tables we've pulled rows from
		# this should be private
		self.readFrom = {
			'Relationship': False,
			'Text': False,
			'Integer': False,
			'Decimal': False
		}
		self.fieldData = {}
		pass

	def __setattribute__(self, name, value):
		dict = object.__getattribute__(self, '__dict__')
		dict['fieldData'][ name ] = value

	def __getattribute__(self, name):
		# need special method for getting field definition
		# this should only get from the instance __dict__['fieldData']
		dict = object.__getattribute__(self, '__dict__')
		if name in dict['fieldData']:
			return dict['fieldData'][ name ]
		else:
			print('not loaded: ' + name)
			return ''
		

	def __fieldDefinition(self, name):

		dict = type(self).__dict__

		if name in dict: # field found in class definition
			return dict[ name ]

		else: # field not found in class definition
			dict = object.__getattribute__(self, '__dict__')
			if name in dict: # field found in Model definition
				return dict[ name ]
			else:
				print('Field not found: ' + name)
			

		return ''

	def read(self, dataType, where):
		if dataType == 'Text':
			rows = self.connection.execute('select * from Text where ')

	def save(self):
		# set createdAt or updatedAt
		pass
		

class Product(Model):
	name = {
		'type': 'text'
	}
	username = {
		'type': 'text'
	}


#conn = sqlite3.connect('test.db')
#Model.connection = conn

u = Product()
a = u.id
a = u.name
a = u.date

u.id = 'hey'
u.name = 'testing'

print(u.name)
