"""
OutputMap:  plugin which takes uncertainty and bias to output a healpix map

Input JSON:
  'action':  'alert', attach to data, and notify
  'res': map resolution; integer number, usually power of 2
  'r': array of detector coordinates (in radians) for triangulation
  'errs': array of detector errors
  'biases': array of detector biases
  'loc': array of supernova location at galactic center (in radians)

Output JSON:
  'm': array representing a Healpix Map
  'map': Healpix Map #may be moved to another plugin
"""
import logging
import numpy as np
import healpy as hp

from snewpdag.dag import Node

class OutputMap(Node):
    def __init__(self, **kwargs):
        self.params = {}
        super().__init__(**kwargs)
        
    def update(self, data):
    
        action = data['action']
        source = data['history'][-1]
        
        if action == 'alert':
            self.params[source] = data #contains res, r, errs, biases, loc
        else:
            logging.error("[{}] Unrecognized action {}".format(self.name, action))
            return
    
        # Construct Output
        ndata ={}
        
        #constants
        r_earth = 6.378 * 10**6
        c = 3. * 10**8
        
        # Set Output Map resolution and convert to pixels
        NSIDE = self.params[source]['resolution']
        NPIX = hp.nside2npix(NSIDE)

        m = np.zeros(NPIX)
        
        # Detector position vectors
        def radius(coords):
        # Returns location of each detector with center of Earth as the origin given coordinates
            return r_earth * np.array((np.cos(coords[0]) * np.cos(coords[1]), np.sin(coords[0]) * np.cos(coords[1]), np.sin(coords[1])))
        det_r = radius(self.params[source]['r'])
        num_det = len(det_r)
        
        
        
        # SN coordinates at galactic center
        sn = self.params[source]['loc']
        # True normal vector from SN direction
        n_sn = -1 * np.array((np.cos(sn[0]) * np.cos(sn[1]), np.sin(sn[0]) * np.cos(sn[1]), np.sin(sn[1])))
       


        
        # Define the chi2 function
        def chi_sq(t0, errs, biases):
            # Finds the chi squared value for given t0, errors, and biases using the Brdar formula
            # Samples random points across the sky and finds the chi squared value. Using this value
            # determines if the point is in 1, 2, or 3 sigma area
            s1 = []
            s2 = []
            s3 = []

            for row in rand:
                # Normal vector for the random supernova location
                n = -1 * np.array((np.cos(row[0]) * np.cos(row[1]), np.sin(row[0]) * np.cos(row[1]), np.sin(row[1])))
                chi = 0
                for i in range(num_det):
                    for j in range(i + 1, len(t0)):
                        r_1 = det_r[i]
                        r_2 = det_r[j]
                        err = errs[i,j]
                        bias = biases[i,j]

                        t_act = np.dot((r_1 - r_2), n_sn)/c
                        t_bf = t_act + bias
                        t = np.dot((r_1 - r_2), n)/c
                        chi += ((t_bf - t)/err)**2
                if chi < 2.3:
                    s1.append(row)
                elif chi < 6.18:
                    s2.append(row)
                elif chi < 11.83:
                    s3.append(row)

            return s1, s2, s3
        
        # Generate random RA/Dec values to calculate chi squared
        ndim = 2
        num = 3000000

        rand = np.random.rand(ndim * num).reshape((num, ndim))
        rand[:,:1] = (rand[:,:1] - 0.5) * 2 * np.pi
        rand[:,1:2] = (rand[:,1:2] - 0.5) *  np.pi
        


        s1,s2,s3 = chi_sq(self.params[source]['t0'],self.[source]['errs'],self.[source]['biases'])
        
        # Transpose sigma areas
        s1 = np.transpose(s1)
        s2 = np.transpose(s2)
        s3 = np.transpose(s3)
        
        # Convert from equatorial to colatitude (theta) and longitude (phi) used by Healpy Mollview
        def Coord_Trans(x, nside):
            theta = -x[1]+np.pi/2
            phi = x[0]+np.pi
            pix = hp.ang2pix(nside,theta,phi)
            return pix

        s1_pix = Coord_Trans(s1,NSIDE)
        s2_pix = Coord_Trans(s2,NSIDE)
        s3_pix = Coord_Trans(s3,NSIDE)
        
        # Make map array. Numbers are arbitrary, simply to provide different colors
        m = np.zeros(NPIX)
        m[s1_pix] = 3
        m[s2_pix] = 2
        m[s3_pix] = 1
        
        # Send to data array
        ndata['m'] = m
        
        # Map visualization -- may be moved to another plugin
        #fig = plt.figure()
        #hp.mollview(m, nest='True')
        #hp.graticule()
        #ndata['map'] = fig



        #notify
        self.notify(ndata)
