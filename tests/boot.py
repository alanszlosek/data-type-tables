from Model import Model
from TreeModel import TreeModel
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

# predefine, so Category can use the class object
class Product(Model):
	pass

class Category(TreeModel):
	name = {
		'type': 'Text'
	}
	Product = {
		'type': 'Relationship',
		#'class': Product,
		'many': True
	}

	def parent(self):
		return self.Category

class Product(Model):
	name = {
		'type': 'Text'
	}
	description = {
		'type': 'Text'
	}
	price = {
		'type': 'Decimal',
		'clean': ''
	}
	Category = {
		'type': 'Relationship'
		#'class': Category
	}


conn = sqlite3.connect('dtt.db')
conn.row_factory = sqlite3.Row

Model.connection = conn
#Model.connection.isolation_level = None
Model.cursor = conn.cursor()
Model.module = __name__
