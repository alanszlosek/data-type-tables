import sqlite3
#import uuid
import random
import datetime
import decimal
decimal.getcontext().prec = 2

# but how can we pull all products?

# what if we did away with Text.type and used Relationship?
# Relationship.key = 'Product'. id='types' and values are all the product ids

class Model:
	connection = object
	tables = ['Relationship','Text','Integer','Decimal']
	queries = []

	# allow id to be passed in, or struct of data
	def __init__(self, id=None):
		load = False
		t = type(id)
		if t is dict:
			instanceDict = object.__getattribute__(self, '__dict__')
			instanceDict.update( id )

		elif t is None:
			#id = random.randrange(0,1000000)
			# hmm, what to do here?
			# make sure doesn't already exist
			pass

		else:
			self.id = id
			load = True
			#print('new ' + str(id))

		self.className = type(self).__name__

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

				# how do i do reverse relationships?
				if 'reverse' in classDict[ key ]:
					objects = []
					related = globals()[ key ]

					# look for current class

					# pull ids for type, and then query ... bah

					query = "select * from Relationship where id<>'type' and key=:key and value=:value"
					data = {'key': self.className, 'value': self.id}

					for row in Model.connection.execute(query, data):
						objects.append( related( row['id'] ) ) 

					Model.queries.append( (query,data) )

					return objects

				else:
					if key in instanceDict:
						id = instanceDict[ key ]
						related = globals()[key] # get class for the related Type
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
                                instanceDict['__pending'] = {}
                        instanceDict['__pending'][ key ] = value
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
			'which': which
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
		className = globals()[ which ]
		for (id, fields) in cache.items():
			objects.append( className( fields ) )
		
		return objects

	def load(self):
		instanceDict = object.__getattribute__(self, '__dict__')
		query = 'select * from Relationship where Relationship.id=:id UNION select * from Text where Text.id=:id UNION select * from Integer where Integer.id=:id UNION select * from Decimal where Decimal.id=:id'
		data = { 'id': self.id }

		Model.queries.append( (query,data) )
		for row in Model.connection.execute(query, data):
			instanceDict[ row['key'] ] = row['value']
		return

	def save(self):
		classDict = type(self).__dict__
		dict = object.__getattribute__(self, '__dict__')

		staging = {
			'Relationship': {},
			'Text': {},
			'Integer': {},
			'Decimal': {}
		}
		
		#print('Saving:')
		for (key,value) in dict['__pending'].items():
			table = classDict[ key ]['type']

			staging[ table ][ key ] = value

		d = datetime.datetime.today()

		data = {
			'id': self.id,
			'type': self.className,
			'type2': 'type',
			'createdAt': d.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': d.strftime('%Y-%m-%d %H:%M:%S')
		}

		cursor = Model.connection.cursor()
		# is object in Relationship?

		query = 'select value from Relationship where id=:type2 and key=:type and value=:id'
		Model.queries.append( (query,data) )

		cursor.execute(query , data)

		if cursor.fetchone() == None:
			query = 'insert into Relationship (id,key,value,createdAt,updatedAt) values(:type2, :type, :id, :createdAt, :updatedAt)'
			cursor.execute(query, data)

			Model.queries.append( (query,data) )
			#print('Bar')
			#print(query)
			#print( repr(data) )

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
					cursor.execute(query, data)

					Model.queries.append( (query,data) )
				else:
					query = 'update ' + table + ' set value=:value, updatedAt=:updatedAt where id=:id and key=:key'
					cursor.execute(query, data)

					Model.queries.append( (query,data) )

		dict['__pending'] = {}

		
class Category(Model):
	name = {
		'type': 'Text'
	}
	parent = {
		'type': 'Relationship'
	}
	Product = {
		'type': 'Relationship',
		'reverse': True # reverse classes don't pre-load
	}

class Product(Model):
	name = {
		'type': 'Text'
	}
	price = {
		'type': 'Decimal',
		'clean': ''
	}
	Category = {
		'type': 'Relationship'
	}


conn = sqlite3.connect('dtt.db')
conn.row_factory = sqlite3.Row

Model.connection = conn

fill = False

if fill:

	categories = {
		'A':'',
		'B':'',
		'C':'',
		'D':''
	}
	for category in categories.keys():
		c = Category()
		c.name = category
		c.save()
		categories[ category ] = c.id

	# create product and assign to category
	i = 0
	while i < 200:
		p = Product()
		p.name = ''.join(random.sample('abcdefghijklmnopqrstuvwxyz ', 15))
		p.price = str(decimal.Decimal(random.randrange(10000))/100)

		which = random.sample( list(categories.values()), 1)
		c = Category( which[0] )

		p.Category = c.id
		p.save()
		
		i += 1


a = False
b = False
c = False
d = False
e = False

if a == True:
	products = Model.get('Product')
	
	p = products[0]
	print('Product ' + p.id)
	print(p.Category.id)

if b == True:
	categories = Model.get('Category')
	cat = Category( categories[0].id )
	products = cat.Product # will return multiple, since it's a reverse relationship
	product = products[0]
	print('Product: ' + product.id)

if c == True:
	products = Model.get('Product')
	for product in products:
		print(product.name + ' ' + str(product.price) )

if d == True:
	categories = Model.get('Category')
	for c in categories:
		print('Products in ' + c.name)
		products = c.Product
		#print( repr(products))
		for prod in products:
			#print( repr(product) )
			n = prod.name
			print( n + ' ' + str(prod.id) )
			
			#print(product.name + ' ' + str(product.price) )
			pass
		print('')


conn.commit()
conn.close()

if False:
	print('Queries: ' + str(len(Model.queries)))
	for query in Model.queries:
		print(query[0])
		print(query[1])
		print('')
