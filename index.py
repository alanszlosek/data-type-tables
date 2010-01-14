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
	def __init__(self, id = None, language = None):
		if id:
			load = True
		else:
			load = False
		self.id = id or random.randrange(0,1000000)
		self.language = language or ''
		self.className = type(self).__name__

		# INTERNALS
		# which tables we've pulled rows from
		# this should be private
		self.readFrom = {
			'Relationship': False,
			'Text': False,
			'Integer': False,
			'Decimal': False
		}

		if load:
			self.read()

		pass
		
	def __getattribute__(self, key):
		#print('getting ' + key)

		classDict = type(self).__dict__
		dict = object.__getattribute__(self, '__dict__')

		if key in classDict and classDict[ key ]['type'] == 'Relationship':
			#print('rel')
			#print( repr(dict))

			# how do i do reverse relationships?
			if 'reverse' in classDict[ key ]:
				objects = []
				related = globals()[ key ]

				# look for current class

				for row in Model.connection.execute('select * from Relationship where key=:key and value=:value', {'key': self.className, 'value': self.id}):
					objects.append( related( row['id'] ) ) 
				return objects

			else:
				if key in dict:
					id = dict[ key ]
					related = globals()[key]
					a = related(id)
					return a

				else:
					return None
			
		else:
			return object.__getattribute__(self, key)

	def __setattr__(self, key, value):
                #print('Setting ' + key)
                # get class dict
                dict = type(self).__dict__

                # if key is in the class dict, then the field was defined and we should prepare it to be saved
                if key in dict:
                        #print('Valid field ' + key)

                        # store the value deep inside the instance dict, which we'll use to create queries
                        dict = object.__getattribute__(self, '__dict__')
                        if not '__pending' in dict:
                                dict['__pending'] = {}
                        dict['__pending'][ key ] = value
                else:
                        #print('Invalid field ' + key)
                        pass

                dict = object.__getattribute__(self, '__dict__')
                dict[ key ] = value

	def get(which, where={}):
		objects = {}

		query = 'select distinct value as id from Relationship where id=:id and key=:key'
		data = {
			'id': 'type',
			'key': which
		}

		c = globals()[ which ]
		# but what if one product doesn't have a name?
		for row in Model.connection.execute(query, data):
			if row['id'] in objects:
				continue
			else:
				objects[ row['id'] ] = c( row['id'] )
			
		
		return objects

	def read(self):
		for table in self.readFrom.keys():
			query = 'select * from ' + table + ' where id=:id'
			#print(query)
			#print(self.id)
			for row in Model.connection.execute(query, {'id':self.id}):
				dict = object.__getattribute__(self, '__dict__')
				dict[ row['key'] ] = row['value']

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
		cursor.execute('select value from Relationship where id=:type2 and key=:type and value=:id', data)
		if cursor.fetchone() == None:
			query = 'insert into Relationship (id,key,value,createdAt,updatedAt) values(:type2, :type, :id, :createdAt, :updatedAt)'
			cursor.execute(query, data)
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

				if cursor.fetchone() == None:
					query = 'insert into ' + table + ' (id,type,key,value,createdAt,updatedAt) values(:id,:type,:key,:value,:createdAt,:updatedAt)'
					cursor.execute(query, data)
				else:
					query = 'update ' + table + ' set value=:value, updatedAt=:updatedAt where id=:id and key=:key'
					cursor.execute(query, data)

		
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


conn = sqlite3.connect('test.db')
conn.row_factory = sqlite3.Row

Model.connection = conn


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

#print( repr(categories) )

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


#p = Product('118577')
#print(p.Category.id)
#c = Category('631419')
#products = c.Product # will return multiple, since it's a reverse relationship

#products = Model.get('Product')
#products = {}
#for product in products.values():
	#print(product.name + ' ' + str(product.price) )

categories = Model.get('Category')
#categories = {}
for c in categories.values():
	print('Products in ' + c.name)
	products = c.Product
	#print( str(len(products)))
	for product in products:
		print(product.name)
		#print(product.name + ' ' + str(product.price) )
	print('')


conn.commit()
conn.close()
