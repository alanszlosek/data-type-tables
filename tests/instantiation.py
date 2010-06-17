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
		classDict = self.cleanDict(classDict)

		self.assertNotEqual(len(classDict.keys()), 0)

	def test_instanceDict(self):
		"""Instance dict should be empty upon instantiation"""
		instanceDict = object.__getattribute__(self.p, '__dict__')
		instanceDict = self.cleanDict(instanceDict)

		self.assertEqual(len(instanceDict.keys()), 0)

	def test_assignment(self):
		self.p.name = 'Testing'
		self.p.foo = 'Bar'

		self.assertTrue(self.p.name == 'Testing')
		self.assertTrue(self.p.foo == 'Bar')

	def test_justOneType(self):
		"""Make sure we only save 1 Type record"""
		self.p.id = 123456789
		self.p.name = 'Testing'
		self.p.save()

		self.p = Product()
		self.p.id = 123456789
		self.p.name = 'Testing'
		self.p.save()

		cursor = Model.Model._connection.cursor()
		cursor.execute('select * from Type where id=:id and type=:type', {'id':123456789, 'type':'Product'})
		rows = cursor.fetchall()
		self.assertEqual(len(rows), 1)

	def test_multipleText(self):
		self.p.id = 123456789
		self.p.name = 'A'
		self.p.save()

		self.p.name = 'B'
		self.p.save()

		cursor = Model.Model._connection.cursor()
		cursor.execute('select * from Text where id=:id and type=:type', {'id':123456789, 'type':'Product'})
		rows = cursor.fetchall()
		self.assertGreater(len(rows), 2)

	def test_delete(self):
		self.p.id = 123456789
		self.p.delete()

		cursor = Model.Model._connection.cursor()

		cursor.execute('select * from Type where id=:id and type=:type', {'id':123456789, 'type':'Product'})
		rows = cursor.fetchall()
		self.assertEqual(len(rows), 0)

		cursor.execute('select * from Text where id=:id and type=:type', {'id':123456789, 'type':'Product'})
		rows = cursor.fetchall()
		self.assertEqual(len(rows), 0)
		

	def cleanDict(self, a):
		b = {}
		for (key,value) in a.items():
			if key[0:1] == '__':
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
