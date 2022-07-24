"""
CelestialPixels - keep maps of ICRS to GCRS directions

to use, just instantiate and call get_map().
If the same (nside,time) is requested, where time is a Unix timestamp to
integer precision (any fractional part is lopped off), then this will
just return one that was created before.
"""
import logging
import numpy as np
import healpy as hp
from astropy import units as u
from astropy.time import Time
from astropy.coordinates import GCRS, SkyCoord, CartesianRepresentation

class CelestialPixels:

  maps = {}

  def __init__(self):
    pass

  def delete_all_maps(self):
    CelestialPixels.maps = {}

  def list_maps(self):
    return CelestialPixels.maps.keys()

  def get_map(self, nside, time):
    """
    Get an array of unit vectors pointing to ICRS skymap pixel centers.
    Arrays are keyed with nside and time.
    If no such array already exists, create one.
    nside = healpix resolution.
    time = Unix timestamp.  Only kept at second granularity.
    """
    time_tag = int(time)
    tag = (nside, time_tag)
    if tag in CelestialPixels.maps:
      return CelestialPixels.maps[tag]

    # need to create a map
    t = Time(time_tag, format='unix')
    npix = hp.nside2npix(nside)
    # pixel centers in ICRS coordinates.
    # c will an array of lon,lat with shape (2,npix).
    c = hp.pixelfunc.pix2ang(nside, range(npix), nest=True, lonlat=True)
    sc = SkyCoord(ra=c[0], dec=c[1], unit=u.deg, frame='icrs', \
                  representation_type='unitspherical', obstime=t)
    gc = sc.transform_to(GCRS)
    # gc is now an array of SkyCoord, but in (ra,dec) in GCRS
    n = gc.represent_as(CartesianRepresentation)
    # n is an array of (x,y,z) unit vectors
    rs = np.stack( (n.x, n.y, n.z) ) # shape (3,npix)
    rs.flags.writeable = False
    CelestialPixels.maps[tag] = rs
    return rs

  def delete_map(self, nside, time):
    time_tag = int(time)
    tag = (nside, time_tag)
    if tag in CelestialPixels.maps:
      del CelestialPixels.maps[tag]

