# A DAG for generating and analyzing two experiment alerts
[
  {
    "name": "Control", "class": "Pass",
    "kwargs": { "line": 100 }
  },

    {"name": "Xenon_val", "class": "gen.Xenon_validator",
     "observe": ["Control"]
     },
    {"name": "JUNO_val", "class": "gen.JUNO_validator",
     "observe": ["Control"]
     },

    {"name": "Baksan_val", "class": "gen.Baksan_validator",
     "observe": ["Control"]
     },
    {"name": "DS20K_val", "class": "gen.DS20K_validator",
     "observe": ["Control"]
     },
    {"name": "DUNE_val", "class": "gen.DUNE_validator",
     "observe": ["Control"]
     },

  {"name": "test_nutime_extraction", "class": "DtsCalculator",
   "observe": ["Xenon_val", "DS20K_val", "Baksan_val", "JUNO_val", "DUNE_val"],
   "kwargs": {'detector_location': 'snewpdag/data/detector_location.csv'}
   },

 {"name": "Diffpoin", "class": "DiffPointing", "observe": ["test_nutime_extraction"],
  "kwargs": {
    "detector_location": "snewpdag/data/detector_location.csv",
    "nside": 32,
    "min_dts": 0,
  }
  },
 { 'name': 'Render', 'class': 'renderers.Skymap', 'observe': [ 'Diffpoin' ],
  'kwargs': { 'in_field': 'map', 'title': 'WMAP band I',
              'filename': 'output/wmap-i.png' }
 }
]

