import Model
import sqlite3
import unittest

class instantiation(unittest.TestCase):
	def setUp(self):
		self.p = Product()
		pass

	def test_subclass(self):
		"""Make sure ORM object is subclass of Model"""
		self.assertTrue(isinstance(self.p, Model.Model))

	def test_classDict(self):
		"""Make sure instance's class dict has fields"""
		classDict = object.__getattribute__(type(self.p), '__dict__')
		# remove all keys with an underscore, as they are internals
		classDict = self.cleanDict(classDict)

		self.assertNotEqual(len(classDict.keys()), 0)

	def test_instanceDict(self):
		"""Instance dict should be empty upon instantiation"""
		instanceDict = object.__getattribute__(self.p, '__dict__')
		instanceDict = self.cleanDict(instanceDict)

		self.assertEqual(len(instanceDict.keys()), 0)

	def test_assignment(self):
		"""Make sure assignment works, and populates the necessary internal data structures"""
		instanceDict = object.__getattribute__(self.p, '__dict__')

		self.p.name = 'Testing'
		self.p.foo = 'Bar'

		self.assertIn('name', instanceDict)
		self.assertIn('foo', instanceDict)
		# should have id, name, foo, language
		self.assertEqual(len(instanceDict['pppending']), 4)
		self.assertSameElements(instanceDict['pppending'], ['id','language','name','foo'])

		self.assertTrue(self.p.name == 'Testing')
		self.assertTrue(self.p.foo == 'Bar')

		

	def test_multipleText(self):
		"""Make sure field revisions are being saved"""
		Model.Model._revisions = True
		self.p.id = 123456789
		self.p.name = 'A'
		self.p.save()

		self.p.name = 'B'
		self.p.save()

		cursor = Model.Model._connection.cursor()
		cursor.execute('select * from Text where id=:id', {'id':123456789, 'type':'Product'})
		rows = cursor.fetchall()
		self.assertEqual(len(rows), 2)

	def test_delete(self):
		"""Make sure deleting an object removes all records from the database"""
		self.p.id = 123456789
		self.p.delete()

		cursor = Model.Model._connection.cursor()

		cursor.execute('select * from Type where id=:id and type=:type', {'id':123456789, 'type':'Product'})
		rows = cursor.fetchall()
		self.assertEqual(len(rows), 0)

		cursor.execute('select * from Text where id=:id', {'id':123456789, 'type':'Product'})
		rows = cursor.fetchall()
		self.assertEqual(len(rows), 0)
		

	def cleanDict(self, a):
		b = {}
		for (key,value) in a.items():
			if key[0:1] == '_':
				continue
			if type(value) is dict:
				b[ key ] = value
		return b
			


class Product(Model.Model):
	name = Model.dttText()
	description = Model.dttText()


conn = sqlite3.connect('dtt.db')
conn.row_factory = sqlite3.Row
Model.Model._connection = conn
Model.Model._module = __name__

if __name__ == '__main__':
	unittest.main()
