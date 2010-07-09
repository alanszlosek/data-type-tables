from Model import Model
from TreeModel import TreeModel
from boot import *

print('Get top Category, print immediate child Categories, three levels')

top = TreeModel.getTree(Category, '')

print(top.name)
for child in top.children():
	print('\t' + child.name)
	for child2 in child.children():
		print('\t\t' + child2.name)


Model.done()
