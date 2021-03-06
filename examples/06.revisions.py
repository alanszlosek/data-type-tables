import time
from Model import Model
from TreeModel import TreeModel
from boot import *

print('New Product, save multiple revisions of its name, pull all')

p = Product()
p.id = 123456789
p.name = 'First'
p.save()

p.name = 'Second'
p.save()

p.name = 'Third'
p.save()

print('Product ' + str(p.id) )
for field in ['name']:
	print('Field: ' + field)
	
	for row in p.fieldRevisions(field):
		print('\t' + row['value'] + ' @' + row['createdAt'])

print('Loaded fields')
p = Product(123456789)
print(p.name)

Model.done()
