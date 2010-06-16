INTRODUCTION
====

Wanted to see first-hand how an ORM would be written that stores data by data type.

WHAT'S IT GOOD FOR?
====

* Allows you to rapidly add data storage to an app
* You get field-level revisions for free, so when you change a Product's name, all previous values are preserved. (Yes, you can turn it off)

DETAILS
====

Tables currently in use:

* Text - for storing text values
* Integer
* Decimal
* Relationship - for relating two objects
* Tree - for creating trees of objects
* Type - for keeping track of object ids and types (class name)

Sample classes: Category and Product

	class Category(HierarchyModel):
		# HierarchyModel is a sub-class of Model
		# extending HierarchyModel gives us parent/child functionality
		name = dttText() # means this value is stored in the Text table
		Product = dttRelationship(many=True) # many=True also makes a pointer from Product back to Category

	class Product(Model):
		name = dttText()
		price = dttDecimal()
		Category = dttRelationship()

They extend Model, which gives them: save(), delete()

Get Product objects for the first Category:

	categories = Model.get(Category)
	products = categories[0].Product

Usage
====

Look at the tests, specifically boot.py for setting up classes, and the individual test files themselves for details.

Tests
====

1. Create an sqlite3 database with reload.sh.
1. Populate the database with: ./t 00
1. Run more tests (01 and so on): ./t 01

Notes
====

You can keep revisions (unofficially) by not passing an id in to the constructor. Pass a dict instead, or just set inst.id=id. When you save, it will avoid creating a duplicate Type record for the id, but will save new records in Integer/Decimal/Text with new dates. I still need to load only the newest dates within load() to further make it work.
