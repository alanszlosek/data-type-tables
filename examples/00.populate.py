import random
import decimal
from Model import Model
from boot import *
decimal.getcontext().prec = 2

def catFill(name, children, parent):
	c = Category()
	c.name = name 
	c.save()
	c.setParent(parent)

	if len(children) > 0:
		for (child, children2) in children.items():
			catFill(child, children2, c)

print('Populating database with Products, Categories, Sub-Categories')
	
categories = {
	'Water': {
		'Ocean': {
			'Indian': {},
			'Atlantic': {}
		},
		'Lake': {
			'Okeechobee': {}
		}
	},
	'Land': {
		'Continent': {
			'North America': {
				'Canada': {},
				'United States': {}
			},
			'Australia': {}
		},
		'Island': {
			'Prince Edward': {}
		}
	}
}

c = Category()
c.name = 'Root'
c.save()
c.makeTree()

for (category,children) in categories.items():
	catFill(category, children, c)

# create product and assign to category

categories = Model.get(Category)

i = 0
while i < 100:
	p = Product()
	# when these save, Category relationship saving messes up
	p.name = ''.join(random.sample('abcdefghijklmnopqrstuvwxyz ', 15))
	p.description = ''.join(random.sample('abcdefghijklmnopqrstuvwxyz ', 20))
	p.price = str(decimal.Decimal(random.randrange(10000))/100)

	category = random.sample(categories, 1)[0]

	p.Category = category
	p.save()

	i += 1

Model.done()
