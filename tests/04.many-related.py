from Model import Model
from boot import *

print('Print Product ids for each Category')

for category in Model.get(Category):
	print(category.name)
	for product in category.Product:
		print('\t' + product.id, product.name)


Model.done()
