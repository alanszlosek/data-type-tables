import Model
from setup00 import *

categories = Model.Model.get('Category')
for c in categories:
	print('Products in ' + c.name)
	products = c.Product
	#print( repr(products))
	for prod in products:
		#print( repr(product) )
		n = prod.name
		print( n + ' ' + str(prod.id) )
		
		#print(product.name + ' ' + str(product.price) )
		pass
	print('')


