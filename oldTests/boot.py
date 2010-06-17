from Model import *
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
	name = dttText()
	Product = dttRelationship(direction='both')

	def parent(self):
		return self.Category

class Product(Model):
	name = dttText()
	description = dttText()
	price = dttDecimal()
	Category = dttRelationship(fetch=1,direction='both')


conn = sqlite3.connect('dtt.db')
conn.row_factory = sqlite3.Row

Model._connection = conn
#Model.connection.isolation_level = None
Model._module = __name__
