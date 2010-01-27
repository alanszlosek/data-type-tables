from Model import Model
from setup00 import *

a = Product()
a.name = 'New Product'
a.save()

id = a.id

b = Product(id)
print(str(b.id) + ': ' + b.name)

