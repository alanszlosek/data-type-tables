import Model
from setup00 import *

# first get top-level categories,
# then print the names of their children to two levels
categories = Model.Model.get('Category')
topCategories = []
for category in categories:
	if category.value('Category') == '0':
		topCategories.append( category )

for category in topCategories:
	print(category.name)
	for child in category.children:
		print("\t" + child.name)
		for child2 in child.children:
			print("\t\t" + child2.name)

