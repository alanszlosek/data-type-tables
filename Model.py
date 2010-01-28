import sys
import random
#import uuid
import datetime
import decimal
decimal.getcontext().prec = 2

class Model:
	connection = object
	module = '__main__' # default module to find classes in
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
			definition = classDict[ key ]
			if definition['type'] == 'Relationship':
				if 'class' in definition:
					# class object was passed in ... makes things easy!
					related = definition['class']
				else:
					# globals() doesn't have the class in scope .... we're in module scope
					related = sys.modules[ Model.module ].__getattribute__(key)

				if key in instanceDict:
					return instanceDict[key]
				else:
					query = 'select * from Relationship where id=:id'
					data = {
						'id': self.id,
						'key': key
					}
					Model.queries.append( (query,data) )

					objects = []
					for row in Model.connection.execute(query, data):
						objects.append( related(row['value']) )

					if 'many' in definition:
						return objects
					elif len(objects) > 0:
						return objects[0]
					else:
						return None

			elif definition['type'] == 'Hierarchy':
				# not the right way to access hierarchy elements
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
			# store the value deep inside the instance dict, which we'll use to create queries
			if not '__pending' in instanceDict:
				instanceDict['__pending'] = []

			if instanceDict['__pending'].count( key ) == 0:
				instanceDict['__pending'].append( key )

			if key == 'Relationship':
				print(value)

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
			'Text': {},
			'Integer': {},
			'Decimal': {}
		}
		relationship = {}
		
		#print('Saving:')
		for key in dict['__pending']:
			table = classDict[ key ]['type']
			if table == 'Relationship':
				relationship[ key ] = self.__getattribute__(key)
			else:
				staging[ table ][ key ] = self.__getattribute__(key)

		#if self.className == 'Product':
		#	print(staging)

		d = datetime.datetime.today()

		data = {
			'id': self.id,
			'type': self.className,
			'createdAt': d.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': d.strftime('%Y-%m-%d %H:%M:%S')
		}

		cursor = Model.connection.cursor()

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
				query = 'select id from ' + table + ' where id=:id and type=:type and key=:key'
				cursor.execute(query, data)

				Model.queries.append( (query,data) )

				if cursor.fetchone() == None:
					query = 'insert into ' + table + ' (id,type,key,value,createdAt,updatedAt) values(:id,:type,:key,:value,:createdAt,:updatedAt)'
					cursor.execute(query, data)
					Model.queries.append( (query,data) )

				else:
					query = 'update ' + table + ' set value=:value, updatedAt=:updatedAt where id=:id and type=:type and key=:key'
					cursor.execute(query, data)
					Model.queries.append( (query,data) )

		# relationship
		table = 'Relationship'
		data['id'] = self.id
		data['type'] = self.className
		for (key,value) in relationship.items():
			data['key'] = key
			data['value'] = value.id

			cursor = Model.connection.cursor()
			# requires exact checking for id,type,key,value, since the first 3 might map a record to many values
			query = 'select id from ' + table + ' where id=:id and type=:type and key=:key and value=:value'
			cursor.execute(query, data)

			Model.queries.append( (query,data) )

			if cursor.fetchone() == None:
				query = 'insert into ' + table + ' (id,type,key,value,createdAt,updatedAt) values(:id,:type,:key,:value,:createdAt,:updatedAt)'
				cursor.execute(query, data)
				Model.queries.append( (query,data) )

			else:
				query = 'update ' + table + ' set value=:value, updatedAt=:updatedAt where id=:id and type=:type and key=:key'
				cursor.execute(query, data)
				Model.queries.append( (query,data) )

		# reverse relationship
		table = 'Relationship'
		data['key'] = self.className
		data['value'] = self.id
		for (key,value) in relationship.items():
			target = sys.modules[ Model.module ].__getattribute__(key)
			targetDict = object.__getattribute__(target, '__dict__')

			if not self.className in targetDict:
				continue

			data['id'] = value.id
			data['type'] = target.__name__

			cursor = Model.connection.cursor()
			query = 'select id from ' + table + ' where id=:id and type=:type and key=:key and value=:value'
			cursor.execute(query, data)

			Model.queries.append( (query,data) )

			if cursor.fetchone() == None:
				query = 'insert into ' + table + ' (id,type,key,value,createdAt,updatedAt) values(:id,:type,:key,:value,:createdAt,:updatedAt)'
				cursor.execute(query, data)
				Model.queries.append( (query,data) )

			else:
				query = 'update ' + table + ' set value=:value, updatedAt=:updatedAt where id=:id and type=:type and key=:key'
				cursor.execute(query, data)
				Model.queries.append( (query,data) )

		dict['__pending'] = []

	def value(self, key):
		instanceDict = object.__getattribute__(self, '__dict__')
		return instanceDict[ key ]
