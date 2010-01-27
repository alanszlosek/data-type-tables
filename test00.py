import Model
import setup00

def catFill(name, children, parent=0):
	c = Category()
	c.name = name 
	c.Category = parent
	c.save()

	if len(children):
		for (child, children2) in children.items():
			catFill(child, children2, c.id)
	
fill = True
if fill == True:
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
				'North America': {},
				'Australia': {}
			},
			'Island': {
				'Prince Edward': {}
			}
		}
	}
	for (category,children) in categories.items():
		catFill(category, children, 0)

	# create product and assign to category

	categories = Model.get('Category')

	i = 0
	while i < 200:
		p = Product()
		p.name = ''.join(random.sample('abcdefghijklmnopqrstuvwxyz ', 15))
		p.price = str(decimal.Decimal(random.randrange(10000))/100)

		category = random.sample(categories, 1)[0]

		p.Category = category.id
		p.save()
		
		i += 1

commit()
