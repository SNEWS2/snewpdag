[
  {
    "name": "Control",
    "class": "Pass",
    "kwargs": { "line": 100 },
  },

  {
    "name": "pickle-in",
    "class": "PickleInput",
    "observe": [ "Control" ],
    "kwargs": {
      "filename": "output/pickle-pickle-0-0.pickle",
    },
  },

  {
    "name": "Dump",
    "class": "Pass",
    "observe": [ "pickle-in" ],
    "kwargs": { "line": 1, "dump": 1 }
  },

  {
    "name": "Diff-dt-h",
    "class": "renderers.Histogram1D",
    "observe": [ "pickle-in" ],
    "kwargs": {
      "title": "Time difference",
      "xlabel": "dt [s]",
      "ylabel": "entries/0.1s",
      "filename": "output/redo-{}-{}-{}.png"
    }
  },

]
