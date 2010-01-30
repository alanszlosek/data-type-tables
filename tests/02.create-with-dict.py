from Model import Model
from boot import *

print('Create Product with a dict, save(), and read back')

data = {
	'id': '99999999',
	'name': 'New Product2'
}
a = Product(data)
a.save()

id = a.id

b = Product(id)
print(str(b.id) + ': ' + b.name)
