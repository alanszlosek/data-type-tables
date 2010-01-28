import sys
import random
#import uuid
import datetime
import decimal
decimal.getcontext().prec = 2

class Model:
	connection = object
	tables = ['Text','Integer','Decimal']
	# Relationship, Type, Hierarchy
	queries = []

	# allow id to be passed in, or struct of data
	def __init__(self, id=None):
		load = False
		t = type(id)
		if t is dict:
			if 'id' in id:
				self.id = id['id']
				del id['id']
				instanceDict = object.__getattribute__(self, '__dict__')
				# set instance variables
				instanceDict.update( id )
				# now push the variables into the pending queue for the save()
				instanceDict['__pending'] = []
				for key in id.keys():
					instanceDict['__pending'].append( key )
			else:
				print('Not passing in a full dataset. id not specified')

		elif id == None:
			self.id = random.randrange(0,1000000)
			# hmm, what to do here?
			# make sure doesn't already exist
			pass

		else:
			self.id = id
			load = True
			#print('new ' + str(id))

		self.className = type(self).__name__
		self.type = type(self)

		if load:
			self.load()

		pass
		
	def __getattribute__(self, key):
		# intercept getting a subclass field definition

		# if key is a field definition, return the value from the instanceDict
		# else, return as normal?

		#print('getting ' + key)

		classDict = type(self).__dict__
		instanceDict = object.__getattribute__(self, '__dict__')

		if key in classDict and type(classDict[ key ]) is dict:
			if classDict[ key ]['type'] == 'Relationship':
				#print('rel')
				#print( repr(dict))

				definition = classDict[ key ]

				# globals() doesn't have the class in scope .... we're in module scope
				if 'className' in definition:
					className = definition['className']
				else:
					className = self.className
				related = sys.modules['__main__'].__getattribute__(key)


				query = 'select * from Relationship where id=:id'
				data = { 'id': self.id }
				Model.queries.append( (query,data) )
				for row in Model.connection.execute(query, data):
					if row['key'] not in instanceDict:
						instanceDict[ row['key'] ] = []
					instanceDict[ row['key'] ].append( row )

				if key in instanceDict:
					id = instanceDict[ key ]
					a = related(id)
					return a

				else:
					return None

			else:
				#print('getting ' + key)

				if key in instanceDict: # not relationship
					return instanceDict[ key ]

				else:
					return None

		else:
			return object.__getattribute__(self, key)

	def __setattr__(self, key, value):
                #print('Setting ' + key)
                # get class dict
		classDict = type(self).__dict__
		instanceDict = object.__getattribute__(self, '__dict__')

		# if key is in the class dict, then the field was defined and we should prepare it to be saved
		if key in classDict:
                        #print('Valid field ' + key)

                        # store the value deep inside the instance dict, which we'll use to create queries
                        if not '__pending' in instanceDict:
                                instanceDict['__pending'] = []
                        instanceDict['__pending'].append( key )
		else:
			#print('Invalid field ' + key)
			pass
		instanceDict[ key ] = value

	def get(which, where={}):
		# better:
		# pull from Relationship and build initial cache level
		# pull from other tables for next cache level
		# for each at first cache level, instantiate and pass in dict of next cache level
		# return
		# at most we'll do N queries, where N is number of tables

		# or unions might help

		queries = []
		for table in Model.tables:
			#queries.append( "select " + table + ".* from " + table + ", Relationship where " + table + ".id=Relationship.value and Relationship.id=:id and Relationship.key=:key" )
			queries.append( "select * from " + table + " where type=:which" )

		query = ' UNION '.join(queries)
		data = {
			'which': which.__name__
		}

		Model.queries.append( (query,data) )

		cache = {}
		for row in Model.connection.execute(query, data):
			id = row['id']
			if not row['id'] in cache:
				cache[ id ] = {}
				cache[ id ]['id'] = id

			cache[ id ][ row['key'] ] = row['value']

		objects = []	
		className = which
		for (id, fields) in cache.items():
			objects.append( className( fields ) )
		
		return objects
	get = staticmethod(get)

	def load(self):
		instanceDict = object.__getattribute__(self, '__dict__')

		query = 'select * from Text where Text.id=:id UNION select * from Integer where Integer.id=:id UNION select * from Decimal where Decimal.id=:id'
		data = { 'id': self.id }
		Model.queries.append( (query,data) )
		for row in Model.connection.execute(query, data):
			instanceDict[ row['key'] ] = row['value']
		return

	def save(self):
		classDict = type(self).__dict__
		dict = object.__getattribute__(self, '__dict__')

		staging = {
			#'Relationship': {},
			'Text': {},
			'Integer': {},
			'Decimal': {}
		}
		
		#print('Saving:')
		for key in dict['__pending']:
			table = classDict[ key ]['type']

			staging[ table ][ key ] = self.__getattribute__(key)

		d = datetime.datetime.today()

		data = {
			'id': self.id,
			'type': self.className,
			'createdAt': d.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': d.strftime('%Y-%m-%d %H:%M:%S')
		}

		cursor = Model.connection.cursor()
		# is object in Relationship?

		query = 'select id from Type where id=:id and name=:type'
		Model.queries.append( (query,data) )

		cursor.execute(query , data)

		if cursor.fetchone() == None:
			query = 'insert into Type (id,name,createdAt) values(:id, :type, :createdAt)'
			cursor.execute(query, data)

			Model.queries.append( (query,data) )

		for (table,fields) in staging.items():
			for (key,value) in fields.items():
				data['key'] = key
				data['value'] = value

				cursor = Model.connection.cursor()
				query = 'select id from ' + table + ' where id=:id'
				cursor.execute(query, data)

				Model.queries.append( (query,data) )

				if cursor.fetchone() == None:
					query = 'insert into ' + table + ' (id,type,key,value,createdAt,updatedAt) values(:id,:type,:key,:value,:createdAt,:updatedAt)'
					print(query)
					print(data)
					cursor.execute(query, data)

					Model.queries.append( (query,data) )
				else:
					query = 'update ' + table + ' set value=:value, updatedAt=:updatedAt where id=:id and key=:key'
					cursor.execute(query, data)

					Model.queries.append( (query,data) )

		dict['__pending'] = []

	def value(self, key):
		instanceDict = object.__getattribute__(self, '__dict__')
		return instanceDict[ key ]
