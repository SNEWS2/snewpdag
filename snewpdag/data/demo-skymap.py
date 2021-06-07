#
# demo for making a picture of a skymap
# before running this,
# wget -c http://lambda.gsfc.nasa.gov/data/map/dr4/skymaps/7yr/raw/wmap_band_iqumap_r9_7yr_W_v4.fits
# into the externals/wmap-fits directory
#
[
{ 'name': 'Input', 'class': 'SkymapInput',
'kwargs': { 'filename': 'externals/wmap-fits/wmap_band_iqumap_r9_7yr_W_v4.fits',
            'out_field': 'skymap' }
},
{ 'name': 'Render', 'class': 'renderers.Skymap', 'observe': [ 'Input' ],
  'kwargs': { 'in_field': 'skymap', 'title': 'WMAP band I',
              'filename': 'output/wmap-i.png' }
}
]
