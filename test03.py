import Model
from setup00 import *

products = Model.Model.get(Product)

p = products[0]
print('Product ' + p.id)
print(p.Category.id)
