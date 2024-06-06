"""
BurstTime - assign burst time using threshold relative to max height.
  Also compare with true time if available.

Arguments:
  twidth:  bin width for initial binning (seconds, default 0.01)
  min_height:  minimum number of events in initial binning, in the highest bin (default 10)
               (if there's background, comparison also done after background subtraction)
  fraction:  event fraction for burst time
  lead_time:  lead time in data to determine background level (sec, default 0)
              set to 0 to use no-background assumption
  height_margin:  height margin in sigma to determine rising edge to peak
                  (default 2)
  bg_margin:  background margin in sigma for estimating total signal
              (default 1)
  in_field:  input field for a new time series (type values.TimeSeries)
  in_truth_field:  input field for true time
  out_field:  output field for burst time
  out_delta_field:  output field for burst - true time
"""
import logging
import numpy as np

from snewpdag.dag import Node
from snewpdag.dag.lib import fetch_field, store_field

class BurstTime(Node):
  def __init__(self, fraction, in_field, in_truth_field,
               out_field, out_delta_field, **kwargs):
    self.fraction = fraction
    self.in_field = in_field
    self.in_truth_field = in_truth_field
    self.out_field = out_field
    self.out_delta_field = out_delta_field
    self.twidth = kwargs.pop('twidth', 0.01)
    self.min_height = kwargs.pop('min_height', 10)
    self.lead_time = kwargs.pop('lead_time', 0.0)
    self.height_margin = kwargs.pop('height_margin', 2.0)
    self.bg_margin = kwargs.pop('bg_margin', 1.0)
    super().__init__(**kwargs)

  def alert(self, data):
    ts, valid = fetch_field(data, self.in_field) # TimeSeries
    if not valid:
      return False

    # bin the time series
    t1 = np.min(ts.times)
    t2 = np.max(ts.times)
    nb = int((t2 - t1) / self.twidth) + 1
    t2a = t1 + nb * self.twidth
    h, edges = ts.histogram(nb, start=t1, stop=t2a)

    # find maximum height, and compare with min_height
    max_height = np.max(h)
    if max_height < self.min_height:
      return False

    logging.debug('{}: nb = {}, max_height = {}'.format(self.name, nb, max_height))

    # find first event which gets max_height - one sigma (sqrt(max_height))
    top = max_height - self.height_margin * np.sqrt(max_height)
    for i in range(len(h)):
      if h[i] > top:
        break
    tf = t1 + (i + 1) * self.twidth
    logging.debug('{}:  i = {}, h = {}'.format(self.name, i, h[:i+1]))
    evs = np.sort(ts.times[ts.times < tf]) # only sort those events before tf

    # if lead_time > 0, estimate background rate/s; otherwise 0
    bg_rate = 0.0
    if self.lead_time == 0.0:
      nf = int(self.fraction * len(evs))

    else:
      tbg = t1 + self.lead_time
      nbg = np.sum([ts.times < tbg])
      bg_rate = nbg / self.lead_time
      logging.debug('{}:  nbg = {}, bg_rate = {}'.format(self.name, nbg, bg_rate))

      # assign time at fraction to burst time
      #
      # prefer to count backwards from end of test interval (up to peak),
      # as we expect the statistical fluctuations with background
      # should affect this count less than counting forward.
      # Counting forward also suffers from the problem that it's unclear
      # from where to start.

      # target signal above pointer
      ntot = len(evs)
      dtt = evs[-1] - evs[0]
      nbgt = dtt * bg_rate
      sigma_nbgt = np.sqrt(nbg) * dtt / self.lead_time
      nsigt = ntot - nbgt - self.bg_margin * sigma_nbgt
      logging.debug('{}:  dtt = {}, lead_time = {}, sigma_nbgt = {}'.format(self.name, dtt, self.lead_time, sigma_nbgt))
      if nsigt < self.min_height:
        return False
      target = (1.0 - self.fraction) * nsigt
      logging.debug('{}:  ntot = {}, nbgt = {}, nsigt = {}, target = {}'.format(self.name, ntot, nbgt, nsigt, target))

      # scan from right
      #   choose the rigthmost event which meets the target
      #   (i.e., signal estimate > target)
      for i in range(int(ntot-target+1), 0, -1):
        neva = ntot - i
        dta = evs[-1] - evs[i]
        nbga = dta * bg_rate
        nsiga = neva - nbga
        logging.debug('{}:    scan neva = {}, dta = {}, nbga = {}, nsiga = {}'.format(self.name, neva, dta, nbga, nsiga))
        if nsiga > target:
          nf = i
          break

      # bisection method
      #   turns out this doesn't work too well, because background
      #   fluctuations cause the signal estimate to jump around quite
      #   a bit, so could randomly find an event where the signal
      #   estimate matches the target.
      #nf = int(ntot / 2)
      #step = nf
      #while step > 0:
      #  neva = ntot - nf # number of events above pointer
      #  dta = evs[-1] - evs[nf] # time interval above pointer
      #  nbga = dta * bg_rate # background estimate above pointer
      #  nsiga = neva - nbga # signal estimate above pointer
      #  step = int(step / 2)
      #  logging.debug('{}:    nf = {}, step = {}, neva = {}, dta = {}, nbga = {}, nsiga = {}'.format(self.name, nf, step, neva, dta, nbga, nsiga))
      #  if nsiga > target:
      #    nf += step
      #  else:
      #    nf -= step

    logging.debug('{}:  top = {}, tf = {}'.format(self.name, top, tf))
    tb = evs[nf]
    logging.debug('tb = {}'.format(tb))
    store_field(data, self.out_field, tb)
    t0, valid = fetch_field(data, self.in_truth_field)
    if valid:
      logging.debug('t0 = {}'.format(t0))
      dt = tb - t0
      store_field(data, self.out_delta_field, dt)
    return True

