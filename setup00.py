import Model
import sqlite3

def commit():
	Model.Model.connection.commit()
	Model.Model.connection.close()
	
def debug():
	print('Queries: ' + str(len(Model.Model.queries)))
	for query in Model.Model.queries:
		print(query[0])
		print(query[1])
		print('')

# predefine, so Category can use the class object
class Product(Model.Model):
	pass

class Category(Model.Model):
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
		'type': 'Hierarchy'
	}
	Product = {
		'type': 'Relationship',
		'class': Product,
		'many': True
		#'reverse': True # reverse classes don't pre-load
	}

	def parent(self):
		return self.Category

class Product(Model.Model):
	name = {
		'type': 'Text'
	}
	price = {
		'type': 'Decimal',
		'clean': ''
	}
	Category = {
		'type': 'Relationship',
		'class': Category
	}


conn = sqlite3.connect('dtt.db')
conn.row_factory = sqlite3.Row

Model.Model.connection = conn
Model.Model.module = __name__
