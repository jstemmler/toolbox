__author__ = 'jstemm'


class NetCDFFile(object):

    def __init__(self, ncfile, **kwargs):

        import pandas as pd
        import numpy as np
        from netCDF import Dataset, num2date

        with Dataset(ncfile, 'r') as D:
            self.varlist = D.variables.keys()