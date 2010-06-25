import sys
import random
#import uuid
import datetime
import decimal
decimal.getcontext().prec = 2

class Model(object):
	_connection = object
	_module = '__main__' # default module to find classes in
	_tables = ['Text','Integer','Decimal']
	# Relationship, Type, Hierarchy
	_debug = False
	_queries = []

	_revisions = None

	# allow id to be passed in, or struct of data
	def __init__(self, id=None):
		instanceDict = object.__getattribute__(self, '__dict__')
		instanceDict['pppending'] = []

		load = False
		t = type(id)
		if t is dict: # passing in a dict does not load anything from the database
			instanceDict.update(id)
			for key in id.keys():
				instanceDict['pppending'].append( key )

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
		self._className = type(self).__name__
		self._type = type(self)

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
				if 'className' in definition:
					# class object was passed in ... makes things easy!
					related = definition['className']
				else:
					# globals() doesn't have the class in scope .... we're in module scope
					related = sys.modules[ Model._module ].__getattribute__(key)

				if key in instanceDict:
					return instanceDict[key]
				else:
					query = 'select * from Relationship where id=:id and type=:type and key=:key'
					data = {
						'id': self.id,
						'type': self._className,
						'key': key
					}
					if self._debug:
						Model._queries.append( (query,data) )

					objects = []
					for row in Model._connection.execute(query, data):
						objects.append( related(row['value']) )

					fetch = definition['fetch']
					if fetch == 0:
						return objects
					else:
						if fetch == 1:
							return objects[0]
						else:
							return objects[0:fetch]

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
		if key[0] != '_' and self.pppending.count(key) == 0:
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
		for table in Model._tables:
			#queries.append( "select " + table + ".* from " + table + ", Relationship where " + table + ".id=Relationship.value and Relationship.id=:id and Relationship.key=:key" )
			queries.append( "select * from " + table + " where type=:which" )

		query = ' UNION '.join(queries)
		data = {
			'which': which.__name__
		}

		if Model._debug:
			Model._queries.append( (query,data) )

		cache = {}
		for row in Model._connection.execute(query, data):
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

		data = { 'id': self.id, 'type': self._className }

		query = 'select id from Type where id=:id and type=:type'
		if self._debug:
			Model._queries.append( (query,data) )
		cursor = Model._connection.execute(query, data)
		row = cursor.fetchone()
		if row != None:
			# ooh, how can i deal with multiple revisions and fields in the same table?
			# what about only loading those fields defined in the class?
			query = 'select * from Text where Text.id=:id and Text.type=:type UNION select * from Integer where Integer.id=:id and Integer.type=:type UNION select * from Decimal where Decimal.id=:id and Decimal.type=:type group by key order by createdAt desc limit 1'
			data = { 'id': self.id, 'type': self._className }
			if self._debug:
				Model._queries.append( (query,data) )
			for row in Model._connection.execute(query, data):
				instanceDict[ row['key'] ] = row['value']
			instanceDict['__exists'] = True
		else:
			instanceDict['__exists'] = False
			
		return

	# should return boolean reflecting success or failure
	def save(self, revisions=None):
		# choose first non-None value from revisions, self.revisions, Model.revisions
		revisions = True
		
		classDict = type(self).__dict__
		instanceDict = object.__getattribute__(self, '__dict__')

		staging = {
			'Text': {},
			'Integer': {},
			'Decimal': {}
		}
		relationship = {}
		

		# group fields to be saved by table and type
		for key in instanceDict['pppending']:
			if not key in classDict: # skip fields not in the class
				continue
			table = classDict[ key ]['type']
			if table == 'Relationship':
				relationship[ key ] = self.__getattribute__(key)
			else:
				staging[ table ][ key ] = self.__getattribute__(key)

		d = datetime.datetime.today()
		when = d.strftime('%Y-%m-%d %H:%M:%S.%f')

		data = {
			'id': self.id,
			'type': self._className,
			'language': self.language,
			'createdAt': when
		}

		# try to update type first, then insert. we only one 1 Type record for an object
		query = 'update Type set updatedAt=:createdAt where id=:id and type=:type'
		if self._debug:
			Model._queries.append( (query,data) )

		cursor = Model._connection.execute(query, data)

		if cursor.rowcount == 0:
			query = 'insert into Type (id,type,createdAt,updatedAt) values(:id, :type, :createdAt, :createdAt)'
			# should check the return value to make sure it worked
			Model._connection.execute(query, data)

			if self._debug:
				Model._queries.append( (query,data) )

		for (table,fields) in staging.items():
			if not fields:
				continue

			# insert multiple rows at one time
			rows = []
			for (key,value) in fields.items():
				data2 = {}
				data2.update( data )
				data2['key'] = key
				data2['value'] = value

				if revisions == False: # only delete old values of fields we're about to save
					query = 'delete from ' + table + ' where id=:id and type=:type and key=:key'
					Model._connection.execute(query, data2)

				# do i need to clone data here?
				rows.append(data2)
			
			query = 'insert into ' + table + ' (id,type,key,value,language,createdAt) values(:id,:type,:key,:value,:language,:createdAt)'
			Model._connection.executemany(query, rows)
			if self._debug:
				Model._queries.append( (query,rows) )

		# relationships
		clearData1 = []
		clearData2 = []
		saveData = []
		for (key,values) in relationship.items():
			relationship = classDict[ key ]
			# need to respect relationship['className'] if present
			clearData1.append( {'id':self.id, 'type':self._className, 'key':key} ) # to
			clearData2.append( {'value':self.id, 'key':self._className, 'type':key} ) # from

			if type(values) is list:
				for value in values:
					saveData.append( {'id':self.id, 'type':self._className, 'key':key, 'value': value.id, 'createdAt':when} )
					saveData.append( {'id':value.id, 'type':type(value).__name__, 'key':self._className, 'value': self.id, 'createdAt':when} )
			else:
				saveData.append( {'id':self.id, 'type':self._className, 'key':key, 'value': values.id, 'createdAt':when} )
				saveData.append( {'id':values.id, 'type':type(values).__name__, 'key':self._className, 'value': self.id, 'createdAt':when} )

		if len(clearData1):
			query = 'delete from Relationship where id=:id and type=:type and key=:key'
			Model._connection.executemany(query, clearData1)
			query = 'delete from Relationship where type=:type and key=:key and value=:value'
			Model._connection.executemany(query, clearData2)

		if len(saveData):
			query = 'insert into Relationship (id,type,key,value,createdAt) values(:id,:type,:key,:value,:createdAt)'
			Model._connection.executemany(query, saveData)

		instanceDict['pppending'] = []
		instanceDict['__exists'] = True

	def delete(self, deep=False):
		tables = ['Type','Decimal','Integer','Text']
		data = { 'id': self.id, 'type': self._className }
		
		# deep is going to be no fun
		for table in tables:
			query = 'delete from ' + table + ' where id=:id and type=:type'
			Model._connection.execute(query, data)

	def value(self, key):
		instanceDict = object.__getattribute__(self, '__dict__')
		return instanceDict[ key ]

	def fieldRevisions(self, key):
		classDict = type(self).__dict__
		if not key in classDict:
			return None

		data = { 'id': self.id, 'type': self._className }
		query = 'select value,createdAt from ' + classDict[ key ]['type'] + ' where id=:id and type=:type order by createdAt desc'
		cursor = Model._connection.execute(query, data)
		return cursor


	def done():
		Model._connection.commit()
		Model._connection.close()
	done = staticmethod(done)


def dttDecimal(validation=None):
	data = {'type': 'Decimal'}
	data.update( locals() )
	return data
def dttInteger(validation=None):
	data = {'type': 'Integer'}
	data.update( locals() )
	return data
def dttText(validation=None):
	data = {'type': 'Text'}
	data.update( locals() )
	return data
def dttRelationship(fetch=0,to=None):
	data = {'type': 'Relationship'}
	data.update( locals() )
	return data
	#, 'fetch': fetch, 'className': to}
