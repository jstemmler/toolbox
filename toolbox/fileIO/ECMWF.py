__author__ = 'Jayson Stemmler'
__created__ = "6/9/15 11:20 AM"

import numpy as np
from netCDF4 import Dataset, num2date

def pick_ecmwf_point(f, v, at=None, LAT=None, LON=None):

    at_times = np.array(at, ndmin=1)
    vout = np.zeros_like(at_times, dtype=float) * np.nan

    def shiftlon(l):
        if 0 <= l <= 180:
            return l
        elif -180 <= l < 0:
            return l + 360.

    with Dataset(f, 'r') as D:
        t = num2date(D.variables['time'][:], D.variables['time'].units)
        if at is not None:
            times = np.in1d(t, at_times)
            d = D.variables[v][times]

        hits = np.array([i in t for i in at_times])

        lat = D.variables['latitude'][:]
        lon = D.variables['longitude'][:]

        lons, lats = np.meshgrid(lon, lat)

        #return lons, lats, shiftlon(LON), LAT

        ix=0

        if isinstance(LAT, float):
            lat_loc = lats == int(LAT)
            lon_loc = lons == int(shiftlon(LON))
            loc = lat_loc & lon_loc
            for i, (a, h) in enumerate(zip(at_times, hits)):
                if h:
                    try:
                        vout[i] = d[ix, loc.nonzero()[0], loc.nonzero()[1]].squeeze()
                    except ValueError:
                        print(ix, loc.nonzero())
                        print(d[ix, loc.nonzero()[0], loc.nonzero()[1]].squeeze())
                        return
                    ix += 1

        elif len(at_times) == len(LAT):
            for i, (a, la, lo, h) in enumerate(zip(at_times, LAT, LON, hits)):
                if h:
                    lat_loc = lats == int(la)
                    lon_loc = lons == int(shiftlon(lo))
                    loc = lat_loc & lon_loc

                    vout[i] = d[ix, loc.nonzero()[0], loc.nonzero()[1]].squeeze()

                    ix += 1
    return vout

def get_ecmwf_grid(file, variable, dtime):
    pass
