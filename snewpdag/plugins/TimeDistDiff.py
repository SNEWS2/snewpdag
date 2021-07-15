"""
TimeDistDiff:  plugin which gives time differences between time distributions

Input JSON: (choose either cl or chi2)

If cl or chi2 are lists rather than numpy arrays, they're converted.
JSON input fields:
    't_low':  low edges of time bins (array of floats)
    't_bins':  number of events in corresponding time bins (array of floats)

Output JSON:
    dictionary of input pairs with time difference (TODO - pyhonise the format)

Data assumptions:
    - it is assumed that both data has 0.1 ms binning
    - both time series do not necessary need to start at the same time, but the time t0 from which t1 and t2 are counted should be the same
    - first 1000 bins of each data have not SN emission (they are used for background calculation)


Authors: V. Kulikovskiy (kulikovs@ge.infn.it), M. Colomer, J. Tseng
The algorithm is adapted from github.com/SNEWS2/lightcurve_match.
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
    source = data['history'].last()
    #source = data['history'][-1]

    if action == 'alert':
      if 't_low' in data and 't_bins' in data:
        self.map[source] = data.copy()
        self.map[source]['history'] = data['history'].copy() # keep local copy
        self.map[source]['valid'] = True
      else:
        logging.error('[{}] Expected t_low and t_bins arrays in time distribution'.format(self.name))
        return
    elif action == 'revoke':
      if source in self.map:
        self.map[source]['valid'] = False
      else:
        logging.error('[{}] Revocation received for unknown source {}'.format(self.name, source))
        return
    elif action == 'reset':
      for source in self.map:
        self.map[source]['valid'] = False
      self.notify(action, data)
      return
    elif action == 'report':
      self.notify(action, data)
      return
    else:
      logging.error("[{}] Unrecognized action {}".format(self.name, action))
      return


    # start constructing output data.
  
    # do the calculation
    #ndata = data.copy()
    result = -9999
    for i in self.map:
        for j in self.map:
            if i < j:
                #here the main time difference calculation comes
                result = gettdelay(self.map[i]['t_low'],self.map[i]['t_bins'],self.map[j]['t_low'],self.map[j]['t_bins'])
    data['tdelay'] = result
    # notify
    # (JCT: notify if have a diff to forward)
    #action_verb = 'revoke' if len(hlist) <= 1 else 'alert'
    hlist = []
    for k in self.map:
      if self.map[k]['valid']:
        hlist.append(self.map[k]['history'])
    if len(hlist) > 1:
      action_verb = 'alert'
      data['history'].combine(hlist)
      self.notify(action_verb, data)
    #print('I notify', data, result)
      
#normalise time series for chi2
#returns err^2 as a second output
def normalizeforchi2(n1,t1,windowleft,windowright):
    nerr1 = n1
    bg = np.mean(n1[0:1000])
    n1 = n1-bg ##background is considered in the first 1000 points of data
    mean = np.sum(n1[(windowleft <= t1) & (t1 <= windowright)])
    if mean < 0: print("WARNING: first 1000 bins of data have abnormal event rate")
    return n1/mean, nerr1/mean/mean

def gettdelay(t1,n1,t2,n2):
    t1 = np.array(t1)
    n1 = np.array(n1)

    t2 = np.array(t2)
    n2 = np.array(n2) 

    tsstep1 = t1[1]-t1[0] #step of the time series
    tsstep2 = t2[1]-t2[0] #step of the time series

    scantmax = 100./1e3 #max window scan in [s]
    scanstep = 0.1/1e3 #scanstep
    windowmax   = 300./1e3 #window where matching is performed
    binsize     = 50./1e3 #bin size - should be multiple of 2*windowmax
    nelements   = int(binsize/tsstep1)

    t1conv = np.convolve(t1, np.ones(nelements+1)/(nelements+1), mode='valid') #running averages - we add +1 to have average in the time series time point
    n1conv = np.convolve(n1, np.ones(nelements+1)/(nelements+1), mode='valid')
    maxt1 = np.mean(t1conv[tuple([n1conv == np.amax(n1conv)])])
    idx = (np.abs(t1 - maxt1)).argmin() #find nearest element to this time
    maxt1 = t1[idx]

    n1,nerr1 = normalizeforchi2(n1,t1,maxt1-windowmax-tsstep1/2.,maxt1+windowmax+tsstep1/2.)
    n2,nerr2 = normalizeforchi2(n2,t2,maxt1-windowmax-tsstep2/2.,maxt1+windowmax+tsstep2/2.)

    minchi2 = float('nan')
    mintdelay = float('nan')

    for tdelay in np.linspace(-scantmax, scantmax, num=int(2*scantmax/scanstep)+1):
        cond1 = tuple([(maxt1 - windowmax + tdelay - tsstep1/2. <= t1) & (t1 <= maxt1 + windowmax + tdelay - tsstep1/2.)])
        cond2 = tuple([(maxt1 - windowmax - tsstep2/2. <= t2) & (t2 <= maxt1 + windowmax - tsstep2/2.)]) #the second detector window stays fixed to fix its background variation
        sample1 = n1[cond1]
        serr1 = nerr1[cond1]

        sample2 = n2[cond2]
        serr2 = nerr2[cond2]

        #drop excess of the elements
        minsize = min(len(sample1),len(sample2))
        minsize = minsize - minsize%nelements
        if len(sample1) != minsize:
            print("Warning - dropping",len(sample1) - minsize,"last element(s) from the first data")
            sample1 = sample1[0:minsize]
            serr1 = serr1[0:minsize]
        if len(sample2) != minsize:
            print("Warning - dropping",len(sample2) - minsize,"last element(s) from the second data")
            sample2 = sample2[0:minsize]
            serr2 = serr2[0:minsize]

        sample1 = np.sum(sample1.reshape(-1, nelements), axis=1)
        serr1 = np.sum(serr1.reshape(-1, nelements), axis=1)
        sample2 = np.sum(sample2.reshape(-1, nelements), axis=1)
        serr2 = np.sum(serr2.reshape(-1, nelements), axis=1)
        errsum = serr1+serr2
        
        chi2 = np.divide(np.power(sample1-sample2,2), errsum, out=np.zeros_like(sample1), where=errsum!=0)
        chi2sum = np.sum(chi2)/len(sample1) #chi2 is normalized to the number of elements since for each shift this can vary
        if not (minchi2 < chi2sum):
            mintdelay = tdelay*1000.
            minchi2   = chi2sum
    print('This is the deltat:', mintdelay)
    #exit()
    return (mintdelay)
