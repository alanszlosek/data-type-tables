from Model import *
import setup00

products = Model.get('Product')
for product in products:
	print(product.name + ' ' + str(product.price) )
