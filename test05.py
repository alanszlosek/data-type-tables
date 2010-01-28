import Model
from setup00 import *

products = Model.Model.get(Product)
for product in products:
	print(product.name + ' ' + str(product.price) )
