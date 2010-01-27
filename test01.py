from Model import *
import setup00

products = Model.get('Product')

p = products[0]
print('Product ' + p.id)
print(p.Category.id)
