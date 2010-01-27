from Model import Model
from setup00 import *

products = Model.get(Product)

p = products[0]
print('Product ' + p.id)
print(p.Category.id)
