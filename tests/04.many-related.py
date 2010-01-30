from Model import Model
from boot import *

print('Get first Category and print Product ids in it')

categories = Model.get(Category)
print('Category:', categories[0].id, categories[0].name)
products = categories[0].Product # will return multiple, since it's a reverse relationship
for product in products:
	print('Product: ' + product.id)
