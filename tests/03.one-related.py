from Model import Model
from boot import *

print('Get first Product, print Category name if any')

products = Model.get(Product)

p = products[0]
print('Product ' + p.id)
cat = p.Category
if cat:
	print(p.Category.id)
else:
	print('No Category')
