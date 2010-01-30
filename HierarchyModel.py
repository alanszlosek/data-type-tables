from Model import Model
import datetime

# what if we did away with Text.type and used Relationship?
# Relationship.key = 'Product'. id='types' and values are all the product ids
# should probably require that the tree name be passed into each of these, because a record might be in more than one tree
class HierarchyModel(Model):
	def __init__(self, id=None):
		super().__init__(id)

		self.getHierarchy()

	def getHierarchy(self):
		query = 'select * from Hierarchy where id=:id'
		data = {
			'id': self.id
		}
		Model.queries.append( (query,data) )

		cursor = Model.connection.cursor()
		cursor.execute(query, data)
		row = cursor.fetchone()
		self.hierarchy = row
		return row

	# need a staticmethod version for creating a tree without an object at the root
	def makeTree(self, name=''):
		d = datetime.datetime.today()
		query = 'insert into Hierarchy (id,type,lft,rgt,tree,createdAt,updatedAt) values(:id,:type,:left,:right,:tree,:createdAt,:updatedAt)'
		data = {
			'id': self.id,
			'type': self.className,
			'left': 1,
			'right': 2,
			'tree': name,
			'createdAt': d.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': d.strftime('%Y-%m-%d %H:%M:%S')
		}	
		Model.connection.execute(query, data)

	def getParent(self):
		if self.hierarchy == None:
			return None
		# but Hierarchy.id might not have a type
		query = 'select type from Hierarchy where id=:parent'
		data = {
			'parent': self.hierarchy['parent']
		}
		Model.queries.append( (query,data) )

		cursor = Model.connection.cursor()
		cursor.execute(query, data)
		row = cursor.fetchone()

		if row == None or row['type'] == '':
			return None

		b = self.type	
		return b( row['id'] )

	def setParent(self, parent):
		if parent == None:
			return
		# set should be an object of the same type as this one	
		parentHierarchy = parent.getHierarchy()

		# begin transaction
		rgt = parentHierarchy['rgt']

		query = 'update Hierarchy set rgt=rgt+2 where rgt >= :right'
		data = {
			'right': rgt
		}
		Model.connection.execute(query, data)
		query = 'update Hierarchy set lft=lft+2 where lft > :right'
		Model.connection.execute(query, data)

		d = datetime.datetime.today()
		query = 'insert into Hierarchy (id,type,lft,rgt,tree,parent,createdAt,updatedAt) values(:id,:type,:left,:right,:tree,:parent,:createdAt,:updatedAt)'
		data = {
			'id': self.id,
			'type': self.className,
			'left': rgt,
			'right': rgt+1,
			'tree': parentHierarchy['tree'],
			'parent': parentHierarchy['id'],
			'createdAt': d.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': d.strftime('%Y-%m-%d %H:%M:%S')
		}	
		Model.connection.execute(query, data)

	def ancestors(self):
		pass
	def parents(self):
		query = 'SELECT parent.name FROM Hierachy AS node, Hierarchy AS parent WHERE node.lft BETWEEN parent.lft AND parent.rgt AND node.id=:id ORDER BY parent.lft'
		data = {
			'id': self.id
		}

		Model.queries.append( (query,data) )

		parents = []
		b = self.type	
		for row in Model.connection.execute(query, data):
			parents.append( b(row) )
		return parents

	def children(self):
		hierarchy = self.getHierarchy()
		
		# would be nice to pull sibling ids and get their fields in one go, maybe by modeling Model.get()?
		query = 'select id from Hierarchy where lft>:left and rgt<:right'
		data = {
			'left': hierarchy['lft'],
			'right': hierarchy['rgt']
			
		}

		Model.queries.append( (query,data) )

		objects = []
		b = self.type	
		for row in Model.connection.execute(query, data):
			objects.append( b(row['id']) )
		return objects 

	def descendents(self):
		hierarchy = self.getHierarchy()
		
		# would be nice to pull sibling ids and get their fields in one go, maybe by modeling Model.get()?
		query = 'select id from Hierarchy where tree=:tree and lft>:left and rgt<:right order by lft'
		data = {
			'tree': hierarchy['tree'],
			'left': hierarchy['lft'],
			'right': hierarchy['rgt']
			
		}

		Model.queries.append( (query,data) )

		objects = []
		b = self.type	
		for row in Model.connection.execute(query, data):
			objects.append( b(row['id']) )
		return objects 

	def siblings(self):
		# hmm, where do we get lft and rgt from? are they already loaded into the instance?
		parent = self.getParent()
		parentHierarcy = parent.getHierarchy()
		
		# would be nice to pull sibling ids and get their fields in one go, maybe by modeling Model.get()?
		query = 'select id from Hierarchy where id<>:id and (lft=rgt+1lft>:left and rgt<:right'
		where = {
			'left': parentHierarchy['lft'],
			'right': parentHierarchy['rgt']
			
		}

		Model.queries.append( (query,data) )

		objects = []
		b = self.type	
		for row in Model.connection.execute(query, data):
			objects.append( b(row['id']) )
		return objects 

	def tree(treeType, name=''):
		# would be nice to pull sibling ids and get their fields in one go, maybe by modeling Model.get()?
		query = 'select id from Hierarchy where lft=1 and type=:type and tree=:tree'
		data = {
			'type': treeType.__name__,
			'tree': name
		}

		Model.queries.append( (query,data) )

		cursor = Model.connection.cursor()
		cursor.execute(query, data)
		row = cursor.fetchone()
		if row == None:
			return None

		b = treeType
		return b( row['id'] )
		
	tree = staticmethod(tree)
