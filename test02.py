import Model
from setup00 import *

data = {
	'id': '99999999',
	'name': 'New Product2'
}
a = Product(data)
a.save()

id = a.id

b = Product(id)
print(str(b.id) + ': ' + b.name)

