"""
Unit tests for CombineMaps node
"""
import unittest
import numpy as np
import healpy as hp
from scipy.stats import chi2
from snewpdag.dag.app import configure, inject
from snewpdag.values import History

class TestCombineMaps(unittest.TestCase):

  def test_convert(self):
    h1 = History()
    h1.append('Input1')
    data = [ { 'action': 'alert', 'ndof': 1, 'history': h1,
               'name': 'Node1' } ]
    npix = hp.nside2npix(2)
    data[0]['chi2'] = (np.arange(npix) * 2 / npix).tolist()
    spec = [ { 'class': 'CombineMaps',
               'name': 'Node1',
               'kwargs': { 'force_cl': True } } ]
    nodes = {}
    nodes[0] = configure(spec)
    inject(nodes, data, spec)
    self.assertEqual(nodes[0]['Node1'].last_data['action'], 'alert')
    self.assertEqual(nodes[0]['Node1'].last_data['history'].emit(), ((('Input1',),),'Node1'))
    self.assertEqual(len(nodes[0]['Node1'].last_data['cl']), npix)
    self.assertEqual(nodes[0]['Node1'].last_data['cl'][0], 0.0)
    self.assertAlmostEqual(nodes[0]['Node1'].last_data['cl'][47], 0.83830832)

  def test_chi2(self):
    spec = [ { 'class': 'CombineMaps', 'name': 'Node1',
               'kwargs': { 'force_cl': False } } ]
    nodes = {}
    nodes[0] = configure(spec)
    npix = hp.nside2npix(2)
    d1 = np.arange(npix) * 2 / npix
    d2 = np.arange(npix) * 3 / npix
    d3 = np.arange(npix) * 4 / npix
    h1 = History()
    h1.append('Input1')
    h2 = History()
    h2.append('Input2')
    h3 = History()
    h3.append('Input3')
    data = [ { 'name': 'Node1', 'action': 'alert', 'history': h1,
               'ndof': 1, 'chi2': d1.tolist() },
             { 'name': 'Node1', 'action': 'alert', 'history': h2,
               'ndof': 2, 'chi2': d2.tolist() },
             { 'name': 'Node1', 'action': 'alert', 'history': h3,
               'ndof': 1, 'chi2': d3.tolist() },
           ]
    inject(nodes, data, spec)
    tdata = nodes[0]['Node1'].last_data
    self.assertEqual(tdata['action'], 'alert')
    self.assertEqual(tdata['history'].emit(),
        ( (('Input1',), ('Input2',), ('Input3',)), 'Node1' ) )
    self.assertNotIn('cl', tdata)
    self.assertEqual(tdata['ndof'], 4)
    self.assertEqual(len(tdata['chi2']), npix)
    td1 = d1 + d2 + d3
    self.assertListEqual(tdata['chi2'].tolist(), td1.tolist())

    # revoke 2nd input
    data = [ { 'name': 'Node1', 'action': 'revoke', 'history': History(('Input2',)) } ]
    inject(nodes, data, spec)
    tdata = nodes[0]['Node1'].last_data
    self.assertEqual(tdata['action'], 'alert')
    self.assertEqual(tdata['history'].emit(),
        ( (('Input1',), ('Input3',)), 'Node1' ) )
    self.assertNotIn('cl', tdata)
    self.assertEqual(tdata['ndof'], 2)
    self.assertEqual(len(tdata['chi2']), npix)
    td2 = d1 + d3
    self.assertListEqual(tdata['chi2'].tolist(), td2.tolist())

    # update 2nd input
    d4 = np.arange(npix) * 5 / npix
    data = [ { 'name': 'Node1', 'action': 'alert', 'history': History(('Input2',)),
               'ndof': 3, 'chi2': d4.tolist() } ]
    inject(nodes, data, spec)
    tdata = nodes[0]['Node1'].last_data
    self.assertEqual(tdata['action'], 'alert')
    self.assertEqual(tdata['history'].emit(),
        ( (('Input1',), ('Input2',), ('Input3',)), 'Node1' ) )
    self.assertNotIn('cl', tdata)
    self.assertEqual(tdata['ndof'], 5)
    self.assertEqual(len(tdata['chi2']), npix)
    td3 = d1 + d4 + d3
    self.assertListEqual(tdata['chi2'].tolist(), td3.tolist())

    # update 3rd input
    d5 = np.arange(npix) * 6 / npix
    data = [ { 'name': 'Node1', 'action': 'alert', 'history': History(('Input1',)),
               'ndof': 2, 'chi2': d5.tolist() } ]
    inject(nodes, data, spec)
    tdata = nodes[0]['Node1'].last_data
    self.assertEqual(tdata['action'], 'alert')
    self.assertEqual(tdata['history'].emit(),
        ( (('Input1',), ('Input2',), ('Input3',)), 'Node1' ) )
    self.assertNotIn('cl', tdata)
    self.assertEqual(tdata['ndof'], 6)
    self.assertEqual(len(tdata['chi2']), npix)
    td4 = d5 + d4 + d3
    self.assertListEqual(tdata['chi2'].tolist(), td4.tolist())

  def test_cl(self):
    spec = [ { 'class': 'CombineMaps', 'name': 'Node1',
               'kwargs': { 'force_cl': False } } ]
    nodes = {}
    nodes[0] = configure(spec)
    npix = hp.nside2npix(2)
    d1 = np.arange(npix) / npix
    d2 = np.arange(npix) * 2 / npix
    d3 = np.arange(npix) * 0.75 / npix
    rv = chi2(2)
    h1 = History()
    h1.append('Input1')
    h2 = History()
    h2.append('Input2')
    h3 = History()
    h3.append('Input3')
    data = [ { 'name': 'Node1', 'action': 'alert', 'history': h1,
               'cl': d1.tolist() },
             { 'name': 'Node1', 'action': 'alert', 'history': h2,
               'ndof': 2, 'chi2': d2.tolist() },
             { 'name': 'Node1', 'action': 'alert', 'history': h3,
               'cl': d3.tolist() },
           ]
    inject(nodes, data, spec)
    tdata = nodes[0]['Node1'].last_data
    self.assertEqual(tdata['action'], 'alert')
    self.assertEqual(tdata['history'].emit(),
        ( (('Input1',), ('Input2',), ('Input3',)), 'Node1' ) )
    self.assertNotIn('ndof', tdata)
    self.assertEqual(len(tdata['cl']), npix)
    td1 = d1 * rv.cdf(d2) * d3
    self.assertListEqual(tdata['cl'].tolist(), td1.tolist())

    # revoke 2nd input
    h4 = History()
    h4.append('Input2')
    data = [ { 'name': 'Node1', 'action': 'revoke', 'history': h4 } ]
    inject(nodes, data, spec)
    tdata = nodes[0]['Node1'].last_data
    self.assertEqual(tdata['action'], 'alert')
    self.assertEqual(tdata['history'].emit(),
        ( (('Input1',), ('Input3',)), 'Node1' ) )
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
    h5 = History()
    h5.append('Input2')
    data = [ { 'name': 'Node1', 'action': 'alert', 'history': h5,
               'cl': d4.tolist() } ]
    inject(nodes, data, spec)
    tdata = nodes[0]['Node1'].last_data
    self.assertEqual(tdata['action'], 'alert')
    self.assertEqual(tdata['history'].emit(),
        ( (('Input1',), ('Input2',), ('Input3',)), 'Node1' ) )
    self.assertNotIn('ndof', tdata)
    self.assertEqual(len(tdata['cl']), npix)
    td3 = d1 * d4 * d3
    self.assertListEqual(tdata['cl'].tolist(), td3.tolist())

    # update 3rd input
    d5 = np.arange(npix) * 6 / npix
    h6 = History()
    h6.append('Input1')
    data = [ { 'name': 'Node1', 'action': 'alert', 'history': h6,
               'ndof': 2, 'chi2': d5.tolist() } ]
    inject(nodes, data, spec)
    tdata = nodes[0]['Node1'].last_data
    self.assertEqual(tdata['action'], 'alert')
    self.assertEqual(tdata['history'].emit(),
        ( (('Input1',), ('Input2',), ('Input3',)), 'Node1' ) )
    #self.assertNotIn('ndof', tdata) ndof will be left over from input
    self.assertEqual(len(tdata['cl']), npix)
    td4 = rv.cdf(d5) * d4 * d3
    self.assertListEqual(tdata['cl'].tolist(), td4.tolist())

  def test_resize_cl(self):
    spec = [ { 'class': 'CombineMaps', 'name': 'Node1',
               'kwargs': { 'force_cl': False } } ]
    nodes = {}
    nodes[0] = configure(spec)
    npix1 = hp.nside2npix(2)
    npix2 = hp.nside2npix(4)
    d1 = np.arange(npix1) * 0.25 / npix1
    d2 = np.arange(npix2) * 0.75 / npix2
    h1 = History()
    h1.append('Input1')
    h2 = History()
    h2.append('Input2')
    data = [ { 'name': 'Node1', 'action': 'alert', 'history': h1,
               'cl': d1.tolist() },
             { 'name': 'Node1', 'action': 'alert', 'history': h2,
               'cl': d2.tolist() }
           ]
    inject(nodes, data, spec)
    tdata = nodes[0]['Node1'].last_data
    self.assertEqual(tdata['action'], 'alert')
    self.assertEqual(tdata['history'].emit(),
        ( (('Input1',), ('Input2',)), 'Node1' ) )
    self.assertNotIn('ndof', tdata)
    self.assertEqual(len(tdata['cl']), npix2)
    td = hp.ud_grade(d1, 4, order_in='NESTED', order_out='NESTED') * d2
    self.assertListEqual(tdata['cl'].tolist(), td.tolist())

  def test_resize_chi2(self):
    spec = [ { 'class': 'CombineMaps', 'name': 'Node1',
               'kwargs': { 'force_cl': False } } ]
    nodes = {}
    nodes[0] = configure(spec)
    npix1 = hp.nside2npix(4)
    npix2 = hp.nside2npix(2)
    d1 = np.arange(npix1) * 2 / npix1
    d2 = np.arange(npix2) * 3 / npix2
    h1 = History()
    h1.append('Input1')
    h2 = History()
    h2.append('Input2')
    data = [ { 'name': 'Node1', 'action': 'alert', 'history': h1,
               'ndof': 1, 'chi2': d1.tolist() },
             { 'name': 'Node1', 'action': 'alert', 'history': h2,
               'ndof': 2, 'chi2': d2.tolist() }
           ]
    inject(nodes, data, spec)
    tdata = nodes[0]['Node1'].last_data
    self.assertEqual(tdata['action'], 'alert')
    self.assertEqual(tdata['history'].emit(),
        ( (('Input1',), ('Input2',)), 'Node1' ) )
    self.assertNotIn('cl', tdata)
    self.assertEqual(len(tdata['chi2']), npix1)
    td1 = d1 + hp.ud_grade(d2, 4, order_in='NESTED', order_out='NESTED')
    self.assertListEqual(tdata['chi2'].tolist(), td1.tolist())

  def test_resize_mixed(self):
    spec = [ { 'class': 'CombineMaps', 'name': 'Node1',
               'kwargs': { 'force_cl': False } } ]
    nodes = {}
    nodes[0] = configure(spec)
    npix1 = hp.nside2npix(4)
    npix2 = hp.nside2npix(2)
    d1 = np.arange(npix1) / npix1
    d2 = np.arange(npix2) * 2 / npix2
    rv = chi2(2)
    h1 = History()
    h1.append('Input1')
    h2 = History()
    h2.append('Input2')
    data = [ { 'name': 'Node1', 'action': 'alert', 'history': h1,
               'cl': d1.tolist() },
             { 'name': 'Node1', 'action': 'alert', 'history': h2,
               'ndof': 2, 'chi2': d2.tolist() }
           ]
    inject(nodes, data, spec)
    tdata = nodes[0]['Node1'].last_data
    self.assertEqual(tdata['action'], 'alert')
    self.assertEqual(tdata['history'].emit(),
        ( (('Input1',), ('Input2',)), 'Node1' ) )
    #self.assertNotIn('ndof', tdata)
    self.assertEqual(len(tdata['cl']), npix1)
    td1 = d1 * hp.ud_grade(rv.cdf(d2), 4, order_in='NESTED', order_out='NESTED')
    self.assertListEqual(tdata['cl'].tolist(), td1.tolist())

