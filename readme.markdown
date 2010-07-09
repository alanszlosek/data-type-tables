INTRODUCTION
====

Wanted to see first-hand how an ORM would be written that stores data by data type, and what the limitations of such a system are.

IT'S HANDY WHEN ...
====

* You want to store your object hierarchy to a database without having to write SQL
* Your app is still in flux and you just want to CRUD without having to create or alter tables to store a new piece of data
* You get field-level revisions for free, so when you change a Product's name and save(), all previous values of name are preserved. (Yes, you can turn it off)

I use this project to save my girlfriend's Etsy store data so I can track changes in her Store sale count and listing view counts. Once I fetch the store data I instantiate a Store object with the Etsy store id, set the object's view count from the API call and save. The save() method doesn't create a new Store object since it already exists in the database. Since field-level revisions are on by default, a new value for "sale count" is saved with a new timestamp. All previous values of "sale count" are preserved with their timestamps. The same goes for each Listing item from the API. New "view counts" are added.

IT'S NOT HANDY WHEN ...
====

* You need to implement search functionality
* Speed is important
* Keeping a small database is important

DETAILS
====

Tables currently in use (see schema.sqlite3):

* Type - for keeping track of object ids and types (class name)
* Text - for storing text values
* Integer
* Decimal
* Relationship - for relating two objects
* Tree - for creating trees of objects

Sample classes: Category and Product

	class Category(TreeModel):
		# TreeModel is a sub-class of Model
		# extending TreeModel gives us parent/child functionality
		name = dttText() # means this value is stored in the Text table
		Product = dttManyRelationship(fetch=0) # fetch all products, and save a pointer from the Product to this Category

	class Product(Model):
		name = dttText()
		price = dttDecimal()
		Category = dttRelationship(fetch=1) # 

They extend Model, which gives them: save(), delete()

Get Product objects for the first Category:

	categories = Model.get(Category)
	products = categories[0].Product

Usage
====

Look at the code the examples folder, specifically boot.py for setting up classes, and the numbered files for details.

Note: when extending the TreeModel class, you must first create an instance of your derived class, save it, and then call INSTANCE.makeTree() to create the root node of the tree. Otherwise calls to setParent() will fail to do anything.

Examples
====

1. Create an sqlite3 database with createDb.sh.
1. Populate the database with: ./runTest.sh 00
1. Run more tests (01 and so on): ./runTest.sh 01

