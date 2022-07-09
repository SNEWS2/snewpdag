"""
Prob2CLMap - take FITS probability maps as input, display in mollview CL
"""
import sys, argparse
import numpy as np
import healpy as hp
import matplotlib.pyplot as plt

def run():
  parser = argparse.ArgumentParser()
  parser.add_argument('inputs', nargs='+', help='input filenames')
  parser.add_argument('-o', '--output', default='output.png',
                      help='output filename')
  parser.add_argument('-t', '--title', default='Probability',
                      help='plot title')
  args = parser.parse_args()

  #cmaps = [ 'Greens', 'Oranges', 'Blues', 'Reds', 'Purples' ]
  #reuse = False
  count = 0
  for input_name in args.inputs:
    print('Input file {}'.format(input_name))
    #hpx = hp.read_map(input_name)
    m, h = hp.fitsfunc.read_map(input_name, dtype=np.float32, hdu=1,
                                h=True, nest=True)
    # calculate CL's
    i = np.flipud(np.argsort(m))
    sorted_levels = np.cumsum(m[i])
    credible_levels = np.empty_like(sorted_levels)
    credible_levels[i] = sorted_levels
    cl = 1.0 - credible_levels

    # combine by adding
    if count == 0:
      clsum = np.zeros_like(cl)
    clsum += cl
    count += 1

  #a = np.full_like(cl, 0.1)
  hp.mollview(clsum,
              title=args.title,
              coord=['C'], unit='CL', min=0.0, max=1.0, nest=True,
              #reuse_axes=reuse,
              #cmap=plt.get_cmap(cmaps[count % len(cmaps)]) ,
              #alpha=a,
              )
  #reuse = True

  print('Output to {}'.format(args.output))
  hp.graticule()
  plt.savefig(args.output)
  return

if __name__ == '__main__':
  run()

