from Model import *

# what if we did away with Text.type and used Relationship?
# Relationship.key = 'Product'. id='types' and values are all the product ids
# should probably require that the tree name be passed into each of these, because a record might be in more than one tree
class HierarchyModel(Model):
	Hierarchy = {
		'type': 'Hierarchy'
	}

	def __init__(self, id=None):
		super().__init__(id)

	def parent(self):
		pass

	def ancestors(self):
		pass
	def parents(self):
		pass

	def children(self):
		pass

	def descendents(self):
		pass

	def siblings(self, tree):
		# hmm, where do we get lft and rgt from? are they already loaded into the instance?
		p = self.parent(tree)
		
		# would be nice to pull sibling ids and get their fields in one go, maybe by modeling Model.get()?
		where = {
			
		}
		objects = self.get(self.className, where)
		return objects 
	
