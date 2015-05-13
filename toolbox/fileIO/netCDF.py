__author__ = 'jstemm'

from netCDF4 import Dataset


class netCDF(object):

    def __init__(self, ncfile, **kwargs):

        import os
        import pandas as pd
        import numpy as np

        self.abspath = os.path.abspath(ncfile)

    def get_keys(self):

        with Dataset(self.abspath, 'r') as D:
            keys = D.variables.keys()
            keys.sort()

        return keys

    def print_vars(self, return_dict=False):
        """Nicely formatted printout of netCDF variables and descriptions
           It will even return the dictionary if you want to reference later,
           just set return_dict to True
        """

        # open the file for reading
        with Dataset(self.abspath, 'r') as D:
            variables = dict()

            # iterate through the keys
            for k in self.get_keys():

                long_name, units, dimensions = None, None, None

                if hasattr(D.variables[k], 'long_name'):
                    long_name = getattr(D.variables[k], 'long_name')

                if hasattr(D.variables[k], 'units'):
                    units = getattr(D.variables[k], 'units')

                if hasattr(D.variables[k], 'dimensions'):
                    dimensions = getattr(D.variables[k], 'dimensions')

                variables[k] = {'long_name': long_name,
                                'dimensions': dimensions,
                                'units': units}

                print('{}\n\tlong name: {}\n\tdimensions: {}\n\tunits: {}'.
                      format(k, long_name, dimensions, units))

        if return_dict:
            return variables
        else:
            return