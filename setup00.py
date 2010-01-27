from Model import *
import sqlite3

def commit():
	Model.connection.commit()
	Model.connection.close()
	
def debug():
	print('Queries: ' + str(len(Model.queries)))
	for query in Model.queries:
		print(query[0])
		print(query[1])
		print('')

class Category(Model):
	name = {
		'type': 'Text'
	}
	# returns an instance of Category
	# :a = self.id
	# :b = key = 'Category'
	# :c = self.className = 'Category'
	# select value from Relationship where id=:a and key=:b and type=:c
	Category = { # parent Category
		# one-to-one mapping
		'type': 'Relationship'
	}
	# :a = self.id
	# :b = className = 'Category'
	# select id from Relationship where value=:a and type=:b and key=:c
	children = {
		'className': 'Category',
		'type': 'Relationship',
		'reverse': True
	}
	Product = {
		'type': 'Relationship',
		'reverse': True # reverse classes don't pre-load
	}

	def parent(self):
		return self.Category

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
