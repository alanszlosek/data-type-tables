import Model
from setup00 import *

categories = Model.Model.get(Category)
cat = Category( categories[0].id )
products = cat.Product # will return multiple, since it's a reverse relationship
for product in products:
	print('Product: ' + product.id)
