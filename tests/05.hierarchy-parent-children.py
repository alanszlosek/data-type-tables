from Model import Model
from HierarchyModel import HierarchyModel
from boot import *

print('Get top Category, print immediate child Categories')

top = HierarchyModel.tree(Category)

print('Top: ' + top.name)
for child in top.children():
	print(child.name)
