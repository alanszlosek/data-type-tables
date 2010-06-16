import sys
import random
#import uuid
import datetime
import decimal
decimal.getcontext().prec = 2

class Model:
	connection = object
	cursor = object
	module = '__main__' # default module to find classes in
	tables = ['Text','Integer','Decimal']
	# Relationship, Type, Hierarchy
	debug = False 
	queries = []

	# allow id to be passed in, or struct of data
	def __init__(self, id=None):
		instanceDict = object.__getattribute__(self, '__dict__')
		instanceDict['pppending'] = []

		load = False
		t = type(id)
		if t is dict: # passing in a dict does not load anything from the database
			instanceDict.update(id)

		elif id == None:
			self.id = random.randrange(0,1000000)
			# hmm, what to do here?
			# make sure doesn't already exist
			pass

		else:
			# this is the only path in which we are certain the record exists in the database
			self.id = id
			load = True
			#print('new ' + str(id))

		# these might conflict with class fields
		self.language = 'en'
		self.className = type(self).__name__
		self.type = type(self)

		if load:
			self.load()

		
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
					if self.debug:
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
				if key in instanceDict: # not relationship
					return instanceDict[ key ]

				else:
					return None

		else:
			return object.__getattribute__(self, key)

	def __setattr__(self, key, value):
		if self.pppending.count(key) == 0:
			self.pppending.append( key ) # shouldn't trigger __setattr__, right?

		return object.__setattr__(self, key, value)

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

		if Model.debug:
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
		# so we can bypass self['_modified']
		instanceDict = object.__getattribute__(self, '__dict__')

		data = { 'id': self.id, 'type': self.className }

		query = 'select id from Type where id=:id and type=:type'
		if self.debug:
			Model.queries.append( (query,data) )
		cursor = Model.connection.execute(query, data)
		row = cursor.fetchone()
		if row != None:
			# ooh, how can i deal with multiple revisions and fields in the same table?
			query = 'select * from Text where Text.id=:id and Text.type=:type UNION select * from Integer where Integer.id=:id and Integer.type=:type UNION select * from Decimal where Decimal.id=:id and Decimal.type=:type'
			data = { 'id': self.id, 'type': self.className }
			if self.debug:
				Model.queries.append( (query,data) )
			for row in Model.connection.execute(query, data):
				instanceDict[ row['key'] ] = row['value']
			instanceDict['__exists'] = True
		else:
			instanceDict['__exists'] = False
			
		return

	# should return boolean reflecting success or failure
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
		for key in dict['pppending']:
			if not key in classDict: # skip fields not in the class
				continue
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
			'language': self.language,
			'createdAt': d.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': d.strftime('%Y-%m-%d %H:%M:%S')
		}

		cursor = Model.cursor

		# make sure we don't add a Type instance more than once
		# but we can add an instance's fields more than once if we want revision-type functionality
		query = 'select id from Type where id=:id and type=:type'
		if self.debug:
			Model.queries.append( (query,data) )

		cursor.execute(query, data)

		if cursor.fetchone() == None:
			query = 'insert into Type (id,type,createdAt) values(:id, :type, :createdAt)'
			cursor.execute(query, data)

			if self.debug:
				Model.queries.append( (query,data) )

		for (table,fields) in staging.items():
			# when inserting we can use the extended insert format
			# we need a broader way to determine whether should be doing an insert, without having to select

			if '__exists' in dict and dict['__exists']:
				for (key,value) in fields.items():
					data['key'] = key
					data['value'] = value

					query = 'update ' + table + ' set value=:value, updatedAt=:updatedAt where id=:id and type=:type and key=:key'
					cursor.execute(query, data)
					if self.debug:
						Model.queries.append( (query,data) )
			elif fields:
				# insert multiple rows at one time
				rows = []
				for (key,value) in fields.items():
					data2 = {}
					data2.update(data)
					data2['key'] = key
					data2['value'] = value

					rows.append(data2)
				
				query = 'insert into ' + table + ' (id,type,key,value,language,createdAt,updatedAt) values(:id,:type,:key,:value,:language,:createdAt,:updatedAt)'
				cursor.executemany(query, rows)
				if self.debug:
					Model.queries.append( (query,rows) )

		# relationship
		table = 'Relationship'
		data['id'] = self.id
		data['type'] = self.className
		for (key,value) in relationship.items():
			data['key'] = key
			data['value'] = value.id

			cursor = Model.cursor
			# requires exact checking for id,type,key,value, since the first 3 might map a record to many values
			query = 'select id from ' + table + ' where id=:id and type=:type and key=:key and value=:value'
			cursor.execute(query, data)

			if self.debug:
				Model.queries.append( (query,data) )

			if cursor.fetchone() == None:
				query = 'insert into ' + table + ' (id,type,key,value,createdAt,updatedAt) values(:id,:type,:key,:value,:createdAt,:updatedAt)'
				cursor.execute(query, data)
				if self.debug:
					Model.queries.append( (query,data) )

			else:
				query = 'update ' + table + ' set value=:value, updatedAt=:updatedAt where id=:id and type=:type and key=:key'
				cursor.execute(query, data)
				if self.debug:
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

			cursor = Model.cursor
			query = 'select id from ' + table + ' where id=:id and type=:type and key=:key and value=:value'
			cursor.execute(query, data)

			if self.debug:
				Model.queries.append( (query,data) )

			if cursor.fetchone() == None:
				query = 'insert into ' + table + ' (id,type,key,value,createdAt,updatedAt) values(:id,:type,:key,:value,:createdAt,:updatedAt)'
				cursor.execute(query, data)
				if self.debug:
					Model.queries.append( (query,data) )

			else:
				query = 'update ' + table + ' set value=:value, updatedAt=:updatedAt where id=:id and type=:type and key=:key'
				cursor.execute(query, data)
				if self.debug:
					Model.queries.append( (query,data) )

		dict['pppending'] = []
		dict['__exists'] = True

	def delete(self, deep=False):
		tables = ['Type','Decimal','Integer','Text']
		data = { 'id': self.id, 'type': self.className }
		for table in tables:
			query = 'delete from ' + table + ' where id=:id and type=:type'
			Model.connection.execute(query, data)

	def value(self, key):
		instanceDict = object.__getattribute__(self, '__dict__')
		return instanceDict[ key ]

	def fieldRevisions(self, key):
		classDict = type(self).__dict__
		if not key in classDict:
			return None

		data = { 'id': self.id, 'type': self.className }
		query = 'select value,createdAt,updatedAt from ' + classDict[ key ]['type'] + ' where id=:id and type=:type order by updatedAt desc'
		cursor = Model.connection.execute(query, data)
		return cursor


	def done():
		Model.connection.commit()
		Model.connection.close()
	done = staticmethod(done)


def dttDecimal(validation=None):
	return {'type': 'Decimal'}
def dttInteger(validation=None):
	return {'type': 'Integer'}
def dttText(validation=None):
	return {'type': 'Text'}
def dttRelationship(many=False):
	return {'type': 'Relationship', 'many': many}
