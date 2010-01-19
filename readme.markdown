INTRODUCTION
====

Wanted to see first-hand how an ORM would be written that stores data by data type.

Sample classes: Category and Product

	class Category(Model):
		name = {
			'type': 'Text' # means this value is stored in the Text table
		}
		parent = {
			'type': 'Relationship'
		}
		Product = {
			'type': 'Relationship',
			'reverse': True # reverse relationships are loaded when they're requested
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

They extend Model, which gives them save() ability.

Get Product objects for the first Category:

	categories = Model.get('Category')
	cat = Category( categories[0].id )
	products = cat.Product
