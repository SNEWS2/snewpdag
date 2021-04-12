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
    "name": "IceCube",
    "class": "gen.TimeSeries",
    "observe": [ "Control" ],
    "kwargs": {
      "mean": 1548.0,
      "seed": 12345,
      "filetype": "tn",
      "filename":
      "snewpdag/data/output_icecube_27_Shen_1D_solar_mass_progenitor.fits_1msbin.txt"
    }
  },

  {
    "name": "JUNO",
    "class": "gen.TimeSeries",
    "observe": [ "Control" ],
    "comment": "do I need to introduce a time delay?",
    "kwargs": {
      "mean": 0.001,
      "seed": 5831,
      "filetype": "tn",
      "filename":
      "snewpdag/data/output_scint20kt_27_Shen_1D_solar_mass_progenitor.fits_1msbin.txt"
    }
  },

  {
    "name": "IceCube-bin",
    "class": "SeriesBinner",
    "observe": [ "IceCube" ],
    "kwargs": {
      "field": "times",
      "nbins": 20000,
      "xlow": -10.0,
      "xhigh": 10.0,
      "xname": "t",
      "yname": "n"
    }
  },

  {
    "name": "JUNO-bin",
    "class": "SeriesBinner",
    "observe": [ "JUNO" ],
    "kwargs": {
      "field": "times",
      "nbins": 20000,
      "xlow": -10.0,
      "xhigh": 10.0,
      "xname": "t",
      "yname": "n"
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
      "field": "tdelay",
      "index": ( "IceCube-bin", "JUNO-bin" ), # delicate because of order?
      "index2": 0,
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
      "field": "tdelay",
      "index": ( "JUNO-bin", "IceCube-bin", ), # test order
      "index2": 1
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
      "field": "times",
      "nbins": 20,
      "xlow": -10.0,
      "xhigh": 10.0,
      "xname": "t",
      "yname": "bins",
      "flags": [ "report", "accumulate", "overflow" ]
    }
  },

  {
    "name": "JUNO-t-render",
    "class": "renderers.Histogram1D",
    "observe": [ "JUNO-t" ],
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
      "field": "times",
      "nbins": 20,
      "xlow": -10.0,
      "xhigh": 10.0,
      "xname": "t",
      "yname": "bins",
      "flags": [ "report", "accumulate", "overflow" ]
    }
  },

  {
    "name": "IceCube-t-render",
    "class": "renderers.Histogram1D",
    "observe": [ "IceCube-t" ],
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
      "field": "dt"
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
  }

]

