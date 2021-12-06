#
# test for GenPoint -> DiffPointing
#

[
  { "name": "Control", "class": "Pass",
    "kwargs": { "line": 100 }
  },
  { "name": "Gen", "class": "gen.GenPoint", "observe": [ "Control" ],
    "kwargs": {
      "detector_location": "snewpdag/data/detector_location.csv",
      "pair_list": [ ('SNOP','Borexino'), ('SNOP','KL'), ('SNOP','KM3') ],
      "ra": -60.0, # like longitude
      "dec": -30.0, # like latitude
      "smear": False,
      "time": "2021-11-01 05:22:36.328",
    }
  },
  { "name": "Gen-out", "class": "Pass", "observe": [ "Gen" ],
    "kwargs": { "line": 1, "dump": 1 }
  },
  { "name": "Diff", "class": "DiffPointing", "observe": [ "Gen" ],
    "kwargs": {
      "detector_location": "snewpdag/data/detector_location.csv",
      "nside": 32,
      "min_dts": 3,
    }
  },
  { "name": "Diff-out", "class": "Pass", "observe": [ "Diff" ],
    "kwargs": { "line": 1, "dump": 1 }
  },
  { "name": "conf", "class": "Chi2CL", "observe": [ "Diff" ],
    "kwargs": { "in_field": "map", "out_field": "clmap" }
  },
  { "name": "skymap", "class": "renderers.Mollview", "observe": [ "conf" ],
    "kwargs": { "in_field": "clmap",
                "title": "DiffPointing",
                "units": "CL", "min": 0, "max": 1,
                "coord": [ 'G' ],
                "filename": "output/test-diff-{}-{}-{}.png" }
  },
  { "name": "fits", "class": "renderers.FitsSkymap", "observe": [ "conf" ],
    "kwargs": { "in_field": "clmap",
                "filename": "output/test-diff-{}-{}-{}.fits" }
  },
]
