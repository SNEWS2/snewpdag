"""
Unit tests for CombineMaps node
"""
import unittest
import numpy as np
import healpy as hp
from scipy.stats import chi2
from snewpdag.dag.app import configure, inject

class TestCombineMaps(unittest.TestCase):

  def test_convert(self):
    data = [ { 'action': 'alert', 'ndof': 1, 'history': ('Input1',),
               'name': 'Node1' } ]
    npix = hp.nside2npix(2)
    data[0]['chi2'] = (np.arange(npix) * 2 / npix).tolist()
    spec = [ { 'class': 'CombineMaps',
               'name': 'Node1',
               'kwargs': { 'force_cl': True } } ]
    nodes = configure(spec)
    inject(nodes, data)
    self.assertEqual(nodes['Node1'].last_data['action'], 'alert')
    self.assertEqual(nodes['Node1'].last_data['history'], (('Input1',),'Node1'))
    self.assertEqual(len(nodes['Node1'].last_data['cl']), npix)
    self.assertEqual(nodes['Node1'].last_data['cl'][0], 0.0)
    self.assertAlmostEqual(nodes['Node1'].last_data['cl'][47], 0.83830832)

  def test_chi2(self):
    spec = [ { 'class': 'CombineMaps', 'name': 'Node1',
               'kwargs': { 'force_cl': False } } ]
    nodes = configure(spec)
    npix = hp.nside2npix(2)
    d1 = np.arange(npix) * 2 / npix
    d2 = np.arange(npix) * 3 / npix
    d3 = np.arange(npix) * 4 / npix
    data = [ { 'name': 'Node1', 'action': 'alert', 'history': ('Input1',),
               'ndof': 1, 'chi2': d1.tolist() },
             { 'name': 'Node1', 'action': 'alert', 'history': ('Input2',),
               'ndof': 2, 'chi2': d2.tolist() },
             { 'name': 'Node1', 'action': 'alert', 'history': ('Input3',),
               'ndof': 1, 'chi2': d3.tolist() },
           ]
    inject(nodes, data)
    tdata = nodes['Node1'].last_data
    self.assertEqual(tdata['action'], 'alert')
    self.assertEqual(tdata['history'],
        ( ('Input1',), ('Input2',), ('Input3',), 'Node1' ) )
    self.assertNotIn('cl', tdata)
    self.assertEqual(tdata['ndof'], 4)
    self.assertEqual(len(tdata['chi2']), npix)
    td1 = d1 + d2 + d3
    self.assertListEqual(tdata['chi2'].tolist(), td1.tolist())

    # revoke 2nd input
    data = [ { 'name': 'Node1', 'action': 'revoke', 'history': ('Input2',) } ]
    inject(nodes, data)
    tdata = nodes['Node1'].last_data
    self.assertEqual(tdata['action'], 'alert')
    self.assertEqual(tdata['history'],
        ( ('Input1',), ('Input3',), 'Node1' ) )
    self.assertNotIn('cl', tdata)
    self.assertEqual(tdata['ndof'], 2)
    self.assertEqual(len(tdata['chi2']), npix)
    td2 = d1 + d3
    self.assertListEqual(tdata['chi2'].tolist(), td2.tolist())

    # update 2nd input
    d4 = np.arange(npix) * 5 / npix
    data = [ { 'name': 'Node1', 'action': 'alert', 'history': ('Input2',),
               'ndof': 3, 'chi2': d4.tolist() } ]
    inject(nodes, data)
    tdata = nodes['Node1'].last_data
    self.assertEqual(tdata['action'], 'alert')
    self.assertEqual(tdata['history'],
        ( ('Input1',), ('Input2',), ('Input3',), 'Node1' ) )
    self.assertNotIn('cl', tdata)
    self.assertEqual(tdata['ndof'], 5)
    self.assertEqual(len(tdata['chi2']), npix)
    td3 = d1 + d4 + d3
    self.assertListEqual(tdata['chi2'].tolist(), td3.tolist())

    # update 3rd input
    d5 = np.arange(npix) * 6 / npix
    data = [ { 'name': 'Node1', 'action': 'alert', 'history': ('Input1',),
               'ndof': 2, 'chi2': d5.tolist() } ]
    inject(nodes, data)
    tdata = nodes['Node1'].last_data
    self.assertEqual(tdata['action'], 'alert')
    self.assertEqual(tdata['history'],
        ( ('Input1',), ('Input2',), ('Input3',), 'Node1' ) )
    self.assertNotIn('cl', tdata)
    self.assertEqual(tdata['ndof'], 6)
    self.assertEqual(len(tdata['chi2']), npix)
    td4 = d5 + d4 + d3
    self.assertListEqual(tdata['chi2'].tolist(), td4.tolist())

  def test_cl(self):
    spec = [ { 'class': 'CombineMaps', 'name': 'Node1',
               'kwargs': { 'force_cl': False } } ]
    nodes = configure(spec)
    npix = hp.nside2npix(2)
    d1 = np.arange(npix) / npix
    d2 = np.arange(npix) * 2 / npix
    d3 = np.arange(npix) * 0.75 / npix
    rv = chi2(2)
    data = [ { 'name': 'Node1', 'action': 'alert', 'history': ('Input1',),
               'cl': d1.tolist() },
             { 'name': 'Node1', 'action': 'alert', 'history': ('Input2',),
               'ndof': 2, 'chi2': d2.tolist() },
             { 'name': 'Node1', 'action': 'alert', 'history': ('Input3',),
               'cl': d3.tolist() },
           ]
    inject(nodes, data)
    tdata = nodes['Node1'].last_data
    self.assertEqual(tdata['action'], 'alert')
    self.assertEqual(tdata['history'],
        ( ('Input1',), ('Input2',), ('Input3',), 'Node1' ) )
    self.assertNotIn('ndof', tdata)
    self.assertEqual(len(tdata['cl']), npix)
    td1 = d1 * rv.cdf(d2) * d3
    self.assertListEqual(tdata['cl'].tolist(), td1.tolist())

    # revoke 2nd input
    data = [ { 'name': 'Node1', 'action': 'revoke', 'history': ('Input2',) } ]
    inject(nodes, data)
    tdata = nodes['Node1'].last_data
    self.assertEqual(tdata['action'], 'alert')
    self.assertEqual(tdata['history'],
        ( ('Input1',), ('Input3',), 'Node1' ) )
    self.assertNotIn('ndof', tdata)
    self.assertEqual(len(tdata['cl']), npix)
    td2 = d1 * d3
    self.assertListEqual(tdata['cl'].tolist(), td2.tolist())
    # other ways to do this assertion.
    # since the calculation here mimics what happens in the calculation,
    # the outputs should (in principle) be exact.
    #self.assertTrue((tdata['cl'] == td2).all())
    #self.assertTrue(np.allclose(tdata['cl'],td2))

    # update 2nd input
    d4 = np.arange(npix) * 0.25 / npix
    data = [ { 'name': 'Node1', 'action': 'alert', 'history': ('Input2',),
               'cl': d4.tolist() } ]
    inject(nodes, data)
    tdata = nodes['Node1'].last_data
    self.assertEqual(tdata['action'], 'alert')
    self.assertEqual(tdata['history'],
        ( ('Input1',), ('Input2',), ('Input3',), 'Node1' ) )
    self.assertNotIn('ndof', tdata)
    self.assertEqual(len(tdata['cl']), npix)
    td3 = d1 * d4 * d3
    self.assertListEqual(tdata['cl'].tolist(), td3.tolist())

    # update 3rd input
    d5 = np.arange(npix) * 6 / npix
    data = [ { 'name': 'Node1', 'action': 'alert', 'history': ('Input1',),
               'ndof': 2, 'chi2': d5.tolist() } ]
    inject(nodes, data)
    tdata = nodes['Node1'].last_data
    self.assertEqual(tdata['action'], 'alert')
    self.assertEqual(tdata['history'],
        ( ('Input1',), ('Input2',), ('Input3',), 'Node1' ) )
    self.assertNotIn('ndof', tdata)
    self.assertEqual(len(tdata['cl']), npix)
    td4 = rv.cdf(d5) * d4 * d3
    self.assertListEqual(tdata['cl'].tolist(), td4.tolist())

