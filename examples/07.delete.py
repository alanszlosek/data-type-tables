from Model import Model
from TreeModel import TreeModel
from boot import *

print('Save New Product then delete')

p = Product()
p.id = 123456789
p.name = 'Delete me'
p.save()

print('Product id ' + str(p.id) )

p.delete()

p = Product(123456789)
if p:
	print(p.name)
else:
	print('Not found')

Model.done()
