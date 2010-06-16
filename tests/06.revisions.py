from Model import Model
from TreeModel import TreeModel
from boot import *

print('New Product, save multiple revisions of its name, pull all')

p = Product()
p.id = 123456789
p.name = 'First'
p.save()

p = Product()
p.id = 123456789
p.name = 'Second'
p.save()

p = Product()
p.id = 123456789
p.name = 'Third'
p.save()

print(p.id)
for row in p.fieldRevisions('name'):
	print('\t' + row['value'] + ' @' + row['updatedAt'])

Model.done()
