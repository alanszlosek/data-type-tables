import time
from Model import Model
from TreeModel import TreeModel
from boot import *

print('New Product, save multiple revisions of its name, pull all')

p = Product()
p.id = 123456789
p.name = 'First'
p.save()

time.sleep(1)

# must re-load instance from scratch to create new revision

p = Product()
p.id = 123456789
p.name = 'Second'
p.save()

time.sleep(1)

p = Product()
p.id = 123456789
p.name = 'Third'
p.save()

print('Product ' + str(p.id) )
for field in ['name']:
	print('Field: ' + field)
	
	for row in p.fieldRevisions(field):
		print('\t' + row['value'] + ' @' + row['updatedAt'])

print('Loaded fields')
p = Product(123456789)
print(p.name)

Model.done()
