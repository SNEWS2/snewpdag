"""
Unit tests for History value object
"""
import unittest

from snewpdag.values import History

class TestHistory(unittest.TestCase):

  def test_init_empty(self):
    h = History()
    self.assertEqual(h.val, [])

  def test_init_list(self):
    d = [ 'testA', 'testB', ('testC', 'testD'), 'testE' ]
    h = History(d)
    self.assertEqual(h.val, d)

  def test_clear(self):
    d = [ 'testA', 'testB', ('testC', 'testD'), 'testE' ]
    h = History(d)
    self.assertEqual(h.val, d)
    h.clear()
    self.assertEqual(h.val, [])

  def test_last(self):
    d = [ 'testA', 'testB', ('testC', 'testD'), 'testE' ]
    h = History(d)
    self.assertEqual(h.last(), 'testE')

  def test_last_tuple(self):
    d = [ 'testA', 'testB', ('testC', 'testD') ]
    h = History(d)
    self.assertEqual(h.last(), ('testC', 'testD'))

  def test_emit(self):
    d = [ 'testA', 'testB', ('testC', 'testD'), 'testE' ]
    h = History(d)
    self.assertEqual(h.emit(), ('testA', 'testB', ('testC', 'testD'), 'testE'))

  def test_str(self):
    d = [ 'testA', 'testB', ('testC', 'testD'), 'testE' ]
    h = History(d)
    self.assertEqual(str(h), "('testA', 'testB', ('testC', 'testD'), 'testE')")

  def test_copy(self):
    d = [ 'testA', 'testB', ('testC', 'testD'), 'testE' ]
    h1 = History(d)
    h2 = h1.copy()
    self.assertEqual(h2.val, d)

  def test_copy_indep(self):
    d1 = [ 'testA', 'testB', ('testC', 'testD'), 'testE' ]
    d2 = [ 'testA', 'testB', ('testC', 'testD'), 'testE', 'testF' ]
    d3 = [ 'testA', 'testB', ('testC', 'testD'), 'testE', 'testG' ]
    h1 = History(d1)
    h2 = h1.copy()
    self.assertEqual(h2.val, d1)
    h1.append('testF')
    self.assertEqual(h1.val, d2)
    self.assertEqual(h2.val, d1)
    h2.append('testG')
    self.assertEqual(h1.val, d2)
    self.assertEqual(h2.val, d3)

  def test_append(self):
    d1 = [ 'testA', 'testB', ('testC', 'testD'), 'testE' ]
    d2 = [ 'testA', 'testB', ('testC', 'testD'), 'testE', 'testF' ]
    h1 = History(d1)
    self.assertEqual(h1.val, d1)
    h1.append('testF')
    self.assertEqual(h1.val, d2)

  def test_combine(self):
    d1 = [ 'testA', 'testB' ]
    d2 = [ 'testC', 'testD' ]
    d3 = [ 'testE', 'testF' ]
    h1 = History(d1)
    h2 = History(d2)
    h3 = History(d3)
    h4 = History()
    h4.combine( [ h1, h2 ] )
    self.assertEqual(h1.val, d1)
    self.assertEqual(h2.val, d2)
    self.assertEqual(h3.val, d3)
    self.assertEqual(h4.val, [ ( ('testA','testB'), ('testC','testD') ) ])
    h1.combine( [ h1, h3 ] )
    self.assertEqual(h2.val, d2)
    self.assertEqual(h3.val, d3)
    self.assertEqual(h4.val, [ ( ('testA','testB'), ('testC','testD') ) ])
    self.assertEqual(h1.val, [ ( ('testA','testB'), ('testE','testF') ) ])

