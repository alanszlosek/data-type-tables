from Model import Model
from boot import *

print('Create Product, save(), and read it back')

a = Product()
a.name = 'New Product'
a.price = 67.01
a.save()

id = a.id

b = Product(id)
print(str(b.id) + ': ' + b.name)
