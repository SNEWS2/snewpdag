#
# a test DAG for generating and analyzing two experiment alerts
#

[
  { # this just triggers generators
    "name": "Control",
    "class": "Pass",
    "kwargs": {
      "line": 100
    }
  },

  {
    "name": "IceCube-ts",
    "class": "gen.TimeSeries",
    "observe": [ "Control" ],
    "kwargs": {
      "mean": 1548.0,
      "sig_filetype": "tn",
      "sig_filename":
      "snewpdag/data/output_icecube_27_Shen_1D_solar_mass_progenitor.fits_1msbin.txt"
    }
  },

  {
    "name": "JUNO-ts",
    "class": "gen.TimeSeries",
    "observe": [ "Control" ],
    "comment": "do I need to introduce a time delay?",
    "kwargs": {
      "mean": 0.001,
      "sig_filetype": "tn",
      "sig_filename":
      "snewpdag/data/output_scint20kt_27_Shen_1D_solar_mass_progenitor.fits_1msbin.txt"
    }
  },

  { "name": "IceCube", "class": "gen.Combine", "observe": [ "IceCube-ts" ] },
  { "name": "JUNO", "class": "gen.Combine", "observe": [ "JUNO-ts" ] },

  {
    "name": "IceCube-bin",
    "class": "SeriesBinner",
    "observe": [ "IceCube" ],
    "kwargs": {
      "in_field": "times",
      "nbins": 20000,
      "xlow": -10.0,
      "xhigh": 10.0,
      "out_xfield": "t",
      "out_yfield": "n"
    }
  },

  {
    "name": "JUNO-bin",
    "class": "SeriesBinner",
    "observe": [ "JUNO" ],
    "kwargs": {
      "in_field": "times",
      "nbins": 20000,
      "xlow": -10.0,
      "xhigh": 10.0,
      "out_xfield": "t",
      "out_yfield": "n"
    }
  },

  {
    "name": "Out1",
    "class": "Pass",
    "observe": [ "JUNO-bin", "IceCube-bin" ],
    "kwargs": {
      "line": 1,
      "dump": 1
    }
  },

  {
    "name": "Diff1",
    "class": "TimeDistDiff",
    "observe": [ "JUNO-bin", "IceCube-bin" ]
  },

  {
    "name": "Out3",
    "class": "Pass",
    "observe": [ "Diff1" ],
    "kwargs": {
      "line": 100,
      "dump": 1
    }
  },

  {
    "name": "Diff1-dt",
    "class": "Histogram1D",
    "observe": [ "Diff1" ],
    "kwargs": {
      "nbins": 100,
      "xlow": -0.1,
      "xhigh": 0.1,
      "in_field": "tdelay",
      "in_index": ( "IceCube-bin", "JUNO-bin" ), # delicate because of order?
      "in_index2": 0,
      "comment": "lists may be delicate because of order"
    }
  },

  {
    "name": "Diff1-dt-render",
    "class": "renderers.Histogram1D",
    "observe": [ "Diff1-dt" ],
    "kwargs": {
      "title": "Time difference",
      "xlabel": "dt [s]",
      "ylabel": "entries/0.1s",
      "filename": "output/gen-test-{}-{}-{}.png"
    }
  },

  {
    "name": "Diff1-chi2",
    "class": "Histogram1D",
    "observe": [ "Diff1" ],
    "kwargs": {
      "nbins": 100,
      "xlow": 0.0,
      "xhigh": 10.0,
      "in_field": "tdelay",
      "in_index": ( "JUNO-bin", "IceCube-bin", ), # test order
      "in_index2": 1
    }
  },

  {
    "name": "Diff1-chi2-render",
    "class": "renderers.Histogram1D",
    "observe": [ "Diff1-chi2" ],
    "kwargs": {
      "title": "chi2",
      "xlabel": "chi2",
      "ylabel": "entries",
      "filename": "output/gen-test-{}-{}-{}.png"
    }
  },

  {
    "name": "JUNO-t",
    "class": "SeriesBinner",
    "observe": [ "JUNO" ],
    "kwargs": {
      "in_field": "times",
      "nbins": 20,
      "xlow": -10.0,
      "xhigh": 10.0,
      "out_xfield": "t",
      "out_yfield": "bins",
      "flags": [ "overflow" ]
    }
  },

  { 'name': 'JUNO-t-acc', 'class': 'BinnedAccumulator',
    'observe': [ 'JUNO-t' ],
    'kwargs': {
      'in_field': 'bins', 'nbins': 20, 'xlow': -10.0, 'xhigh': 10.0,
      'out_xfield': 't', 'out_yfield': 'bins',
      'flags': [ 'overflow' ],
    }
  },

  {
    "name": "JUNO-t-render",
    "class": "renderers.Histogram1D",
    "observe": [ "JUNO-t-acc" ],
    "kwargs": {
      "title": "JUNO time profile",
      "xlabel": "time [s]",
      "ylabel": "entries/0.1s",
      "filename": "output/gen-test-{}-{}-{}.png"
    }
  },

  {
    "name": "IceCube-t",
    "class": "SeriesBinner",
    "observe": [ "IceCube" ],
    "kwargs": {
      "in_field": "times",
      "nbins": 20,
      "xlow": -10.0,
      "xhigh": 10.0,
      "out_xfield": "t",
      "out_yfield": "bins",
      "flags": [ "overflow" ]
    }
  },

  { 'name': 'IceCube-t-acc', 'class': 'BinnedAccumulator',
    'observe': [ 'IceCube-t' ],
    'kwargs': {
      'in_field': 'bins', 'nbins': 20, 'xlow': -10.0, 'xhigh': 10.0,
      'out_xfield': 't', 'out_yfield': 'bins',
      'flags': [ 'overflow' ],
    }
  },

  {
    "name": "IceCube-t-render",
    "class": "renderers.Histogram1D",
    "observe": [ "IceCube-t-acc" ],
    "kwargs": {
      "title": "IceCube time profile",
      "xlabel": "time [s]",
      "ylabel": "entries/0.1s",
      "filename": "output/gen-test-{}-{}-{}.png"
    }
  },

  {
    "name": "Out-t",
    "class": "Pass",
    "observe": [ "JUNO", "IceCube" ],
    "kwargs": {
      "line": 100,
      "dump": 1
    }
  },

  {
    "name": "Diff2",
    "class": "NthTimeDiff",
    "observe": [ "JUNO", "IceCube" ],
    "kwargs": {
      "nth": 1
    }
  },

  {
    "name": "Out2",
    "class": "Pass",
    "observe": [ "Diff2" ],
    "kwargs": {
      "line": 100,
      "dump": 1
    }
  },

  {
    "name": "Diff2-dt",
    "class": "Histogram1D",
    "observe": [ "Diff2" ],
    "kwargs": {
      "nbins": 100,
      "xlow": -0.1,
      "xhigh": 0.1,
      "in_field": "dt"
    }
  },

  {
    "name": "Diff2-dt-render",
    "class": "renderers.Histogram1D",
    "observe": [ "Diff2-dt" ],
    "kwargs": {
      "title": "Time difference",
      "xlabel": "dt [s]",
      "ylabel": "entries/0.1s",
      "filename": "output/gen-test-{}-{}-{}.png"
    }
  },

]

