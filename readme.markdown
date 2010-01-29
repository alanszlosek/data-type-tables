INTRODUCTION
====

Wanted to see first-hand how an ORM would be written that stores data by data type.

Sample classes: Category and Product

	class Category(HierarchyModel):
		# HierarchyModel is a sub-class of Model
		# extending HierarchyModel gives us parent/child functionality
		name = {
			'type': 'Text' # means this value is stored in the Text table
		}
		Product = {
			'type': 'Relationship',
			'many': True
		}

	class Product(Model):
		name = {
			'type': 'Text'
		}
		price = {
			'type': 'Decimal'
		}
		Category = {
			'type': 'Relationship'
		}

They extend Model, which gives them save() ability.

Get Product objects for the first Category:

	categories = Model.get(Category)
	products = categories[0].Product

Usage
====

1. Create an sqlite3 database with reload.sh.
1. Run: python3 ./test00.py
1. Select another test to run: test01.py through test08.py
