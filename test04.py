import Model
from setup00 import *

categories = Model.Model.get(Category)
cat = Category( categories[0].id )
products = cat.Product # will return multiple, since it's a reverse relationship
product = products[0]
print('Product: ' + product.id)
