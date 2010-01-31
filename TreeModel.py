from Model import Model
import datetime

# what if we did away with Text.type and used Relationship?
# Relationship.key = 'Product'. id='types' and values are all the product ids
# should probably require that the tree name be passed into each of these, because a record might be in more than one tree
class TreeModel(Model):
	def __init__(self, id=None):
		super().__init__(id)

		self.getHierarchy()

	def getHierarchy(self):
		query = 'select * from Tree where id=:id'
		data = {
			'id': self.id
		}
		Model.queries.append( (query,data) )

		cursor = Model.connection.cursor()
		cursor.execute(query, data)
		row = cursor.fetchone()
		self.hierarchy = row

	# need a staticmethod version for creating a tree without an object at the root
	def makeTree(self, name=''):
		d = datetime.datetime.today()
		query = 'insert into Tree (id,type,lft,rgt,name,createdAt,updatedAt) values(:id,:type,:left,:right,:name,:createdAt,:updatedAt)'
		data = {
			'id': self.id,
			'type': self.className,
			'left': 1,
			'right': 2,
			'name': name,
			'createdAt': d.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': d.strftime('%Y-%m-%d %H:%M:%S')
		}	
		Model.connection.execute(query, data)
		self.getHierarchy()

	def getParent(self):
		if self.hierarchy == None or self.hierarchy['parent'] == '':
			return None

		b = self.type	
		return b( self.hierarchy['parent'] )

	def setParent(self, parent):
		if parent == None:
			return
		# set should be an object of the same type as this one	
		parentHierarchy = parent.hierarchy

		# begin transaction
		rgt = parentHierarchy['rgt']

		query = 'update Tree set rgt=rgt+2 where rgt >= :right'
		data = {
			'right': rgt
		}
		Model.connection.execute(query, data)
		query = 'update Tree set lft=lft+2 where lft > :right'
		Model.connection.execute(query, data)

		d = datetime.datetime.today()
		query = 'insert into Tree (id,type,lft,rgt,name,parent,createdAt,updatedAt) values(:id,:type,:left,:right,:name,:parent,:createdAt,:updatedAt)'
		data = {
			'id': self.id,
			'type': self.className,
			'left': rgt,
			'right': rgt+1,
			'name': parentHierarchy['name'],
			'parent': parentHierarchy['id'],
			'createdAt': d.strftime('%Y-%m-%d %H:%M:%S'),
			'updatedAt': d.strftime('%Y-%m-%d %H:%M:%S')
		}	
		Model.connection.execute(query, data)
		self.getHierarchy()

	def ancestors(self):
		pass
	def parents(self):
		query = 'SELECT parent.id FROM Tree AS node, Tree AS parent WHERE node.name=:name and parent.name=:name and node.lft BETWEEN parent.lft AND parent.rgt AND node.id=:id ORDER BY parent.lft'
		data = {
			'id': self.id,
			'name': self.hierarchy['name']
		}

		Model.queries.append( (query,data) )

		parents = []
		b = self.type	
		for row in Model.connection.execute(query, data):
			parents.append( b( row['id'] ) )
		return parents

	def children(self):
		# would be nice to pull sibling ids and get their fields in one go, maybe by modeling Model.get()?
		query = 'select id from Tree where name=:name and parent=:parent'
		data = {
			'name': self.hierarchy['name'],
			'parent': self.id
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
		query = 'select id from Tree where name=:name and lft>:left and rgt<:right order by lft'
		data = {
			'name': hierarchy['name'],
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
		query = 'select id from Tree where parent=:parent and id<>:id'
		where = {
			'parent': self.hierarchy['parent'],
			'name': self.hierarchy['name']
			
		}

		Model.queries.append( (query,data) )

		objects = []
		b = self.type	
		for row in Model.connection.execute(query, data):
			objects.append( b( row['id'] ) )
		return objects 

	def getTree(treeType, name=''):
		# would be nice to pull sibling ids and get their fields in one go, maybe by modeling Model.get()?
		query = 'select id from Tree where lft=1 and type=:type and name=:name'
		data = {
			'type': treeType.__name__,
			'name': name
		}
		Model.queries.append( (query,data) )

		cursor = Model.connection.cursor()
		cursor.execute(query, data)
		row = cursor.fetchone()
		if row == None:
			return None

		return treeType( row['id'] )
		
	getTree = staticmethod(getTree)
