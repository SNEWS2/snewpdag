#
# a test DAG for generating and analyzing two experiment alerts
#

[
  {
    "name": "Control", "class": "Pass",
    "kwargs": { "line": 100 }
  },

  {
    "name": "JUNO", "class": "gen.GenerateSGBG",
    "observe": [ "Control" ],
    "kwargs": {
      "mean": 3e3, "seed": 5831, "bg": 0.001,
      "filetype": "tn", "filename":
      "snewpdag/data/output_scint20kt_27_Shen_1D_solar_mass_progenitor.fits_1msbin.txt"
    }
  },

  {
    "name": "JUNO-out", "class": "Pass",
    "observe": [ "JUNO" ],
    "kwargs": { "line": 1, "dump": 1 }
  },

  {
    "name": "JUNO-bin", "class": "BinnedAccumulator",
    "observe": [ "JUNO" ],
    "kwargs": {
      "field": "times",
      "nbins": 20000, "xlow": -10.0, "xhigh": 10.0,
      "xname": "t", "yname": "bins",
      'flags': [ 'overflow' ],
    }
  },

  {
    "name": "JUNO-bin-out", "class": "Pass",
    "observe": [ "JUNO-bin" ],
    "kwargs": { "line": 1, "dump": 1 }
  },

  {
    "name": "JUNO-bin-h",
    "class": "renderers.Histogram1D",
    "observe": [ "JUNO-bin" ],
    "kwargs": {
      "title": "JUNO time profile",
      "xlabel": "time [s]",
      "ylabel": "entries/0.1s",
      "filename": "output/gen-liq-{}-{}-{}.png"
    }
  },

  {
    "name": "SNOP", "class": "gen.GenerateSGBG",
    "observe": [ "Control" ],
    "kwargs": {
      "mean": 5e5, "seed": 1235, "bg": 1548,
      "filetype": "tn", "filename":
      "snewpdag/data/output_icecube_27_Shen_1D_solar_mass_progenitor.fits_1msbin.txt"
    }
  },

  {
    "name": "SNOP-out", "class": "Pass",
    "observe": [ "SNOP" ],
    "kwargs": { "line": 1, "dump": 1 }
  },

  {
    "name": "SNOP-bin", "class": "BinnedAccumulator",
    "observe": [ "SNOP" ],
    "kwargs": {
      "field": "times",
      "nbins": 20000, "xlow": -10.0, "xhigh": 10.0,
      "xname": "t", "yname": "bins",
      'flags': [ 'overflow' ],
    }
  },

  {
    "name": "SNOP-bin-out", "class": "Pass",
    "observe": [ "SNOP-bin" ],
    "kwargs": { "line": 1, "dump": 1 }
  },

  {
    "name": "SNOP-bin-h", "class": "renderers.Histogram1D",
    "observe": [ "SNOP-bin" ],
    "kwargs": {
      "title": "SNOP time profile",
      "xlabel": "time [s]",
      "ylabel": "entries/1 ms",
      "filename": "output/gen-liq-{}-{}-{}.png"
    }
  },

  {
    "name": "Diff", "class": "NthTimeDiff",
    "observe": [ "JUNO", "SNOP" ],
    "kwargs": { "nth": 1 }
  },

  {
    "name": "Diff-out", "class": "Pass",
    "observe": [ "Diff" ],
    "kwargs": { "line": 100, "dump": 1 }
  },

  {
    "name": "Diff-dt", "class": "Histogram1D",
    "observe": [ "Diff" ],
    "kwargs": {
      "field": "dt",
      "nbins": 100, "xlow": -0.1, "xhigh": 0.1,
    }
  },

  {
    "name": "Diff-dt-out", "class": "Pass",
    "observe": [ "Diff-dt" ],
    "kwargs": { "line": 100, "dump": 1 }
  },

  {
    "name": "Diff-dt-h",
    "class": "renderers.Histogram1D",
    "observe": [ "Diff-dt" ],
    "kwargs": {
      "title": "Time difference",
      "xlabel": "dt [s]",
      "ylabel": "entries/1 ms",
      "filename": "output/gen-liq-{}-{}-{}.png"
    }
  }

]

