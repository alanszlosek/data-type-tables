import Model
import HierarchyModel
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

class Category(HierarchyModel.HierarchyModel):
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

class Product(Model.Model):
	name = {
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

Model.Model.connection = conn
Model.Model.connection.isolation_level = None
Model.Model.module = __name__
