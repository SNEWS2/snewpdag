"""
TimeDistDiff:  plugin which gives time differences between time distributions

Input JSON: (choose either cl or chi2)

If cl or chi2 are lists rather than numpy arrays, they're converted.
JSON input fields:
    't':  low edges of time bins (array of floats)
    'n':  number of events in corresponding time bins (array of floats)

Output JSON:
    dictionary of input pairs with time difference (TODO - pyhonise the format)

Author: V. Kulikovskiy (kulikovs@ge.infn.it)
"""
import logging
import numpy as np

from snewpdag.dag import Node

class TimeDistDiff(Node):
  def __init__(self, **kwargs):
    self.map = {}
    super().__init__(**kwargs)

  def update(self, data):
    action = data['action']
    source = data['history'][-1]
 
    if action == 'alert':
      if 't' in data and 'n' in data:
        self.map[source] = data
        self.map[source]['valid'] = True
      else:
        logging.error('[{}] Expected t and n arrays in time distribution'.format(self.name))
        return
    elif action == 'revoke':
      if source in self.map:
        self.map[source]['valid'] = False
      else:
        logging.error('[{}] Revocation received for unknown source {}'.format(self.name, source))
        return
    else:
      logging.error("[{}] Unrecognized action {}".format(self.name, action))
      return


    # start constructing output data.
    ndata = {}

    # first, see if there are at least two valid data sets.  if so, alert. otherwise revoke.
    hlist = []
    for k in self.map:
      if self.map[k]['valid']:
        hlist.append(self.map[k]['history'])
    ndata['action'] = 'revoke' if len(hlist) <= 1 else 'alert'
    ndata['history'] = tuple(hlist)

    ndata['tdelay'] = {}
    # do the calculation
    for i in self.map:
        for j in self.map:
            if i < j:
                #here the main time difference calculation comes
                ndata['tdelay'][(i,j)] = gettdelay(self.map[i]['t'],self.map[i]['n'],self.map[j]['t'],self.map[j]['n'])

    # notify
    self.notify(ndata)

def normalizeforchi2(n1):
    n1 = n1-np.mean(n1[0:int(len(n1)/10)]) #background is concidered in the first 10% of the data
    mean = np.mean(n1)
    if mean < 0: print("WARNING: 10% of the data have abnormal even rate")
    return n1/mean

def gettdelay(t1,n1,t2,n2):
    t1 = np.array(t1)
    n1 = np.array(n1)
    n1 = normalizeforchi2(n1)

    t2 = np.array(t2)
    n2 = np.array(n2) 
    n2 = normalizeforchi2(n2)

    scantmax = 100./1e3 #max window scan in [s]
    scanstep = 0.1/1e3 #scanstep
    windowmax   = 300./1e3 #window where matching is performed
    binsize     = 50./1e3 #bin size - should be multiple of 2*windowmax
    nelements   = int(2*windowmax/binsize)
    #print("elements in",-windowmax, windowmax, binsize, "are",nelements)

    t1resample = t1[0:len(t1)-len(t1)%nelements]
    t1resample = np.mean(np.array(t1resample).reshape(-1, nelements), axis=1)
    n1resample = n1[0:len(n1)-len(n1)%nelements]
    n1resample = np.sum(np.array(n1resample).reshape(-1, nelements), axis=1)
    maxt1 = np.mean(t1resample[tuple([n1resample == np.amax(n1resample)])])

    #maxt1 = np.mean(t1[tuple([n1 == np.amax(n1)])])
    #print("maxt1",maxt1)
    minchi2 = float('nan')
    mintdelay = float('nan')
    for tdelay in np.linspace(-scantmax, scantmax, int(2*scantmax/scanstep)+1):
        #print("tdelay",tdelay)
        cond1 = tuple([(maxt1 - windowmax + tdelay <= t1) & (t1 <= maxt1 + windowmax + tdelay)])
        cond2 = tuple([(maxt1 - windowmax <= t2) & (t2 <= maxt1 + windowmax )]) #the second detector window stays fixed to fix its background variation
        sample1 = n1[cond1]
        sample2 = n2[cond2]
        #print(len(sample1),len(sample2))
        #drop excess of the elements
        minsize = min(len(sample1),len(sample2))
        sample1 = sample1[0:minsize]
        sample2 = sample2[0:minsize]
        #print(len(sample1),len(sample2))
        if len(sample1)%nelements != 0:
            #print("Warning - dropping",len(sample1)%nelements,"elements from the first data")
            sample1 = sample1[0:len(sample1)-len(sample1)%nelements]
        if len(sample2)%nelements != 0:
            #print("Warning - dropping",len(sample2)%nelements,"last elements from the second data")
            sample2 = sample2[0:len(sample2)-len(sample2)%nelements]
        sample1 = np.sum(np.array(sample1).reshape(-1, nelements), axis=1)
        sample2 = np.sum(np.array(sample2).reshape(-1, nelements), axis=1)
        chi2 = np.sum(np.power(sample1-sample2,2))/len(sample1) #chi2 is normalized to the number of elements since for each shift this can vary
        if not (minchi2 < chi2):
            mintdelay = tdelay
            minchi2   = chi2
    return (mintdelay,minchi2)
