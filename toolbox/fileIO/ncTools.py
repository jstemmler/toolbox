__author__ = 'jstemm'


class NetCDFFile(object):

    def __init__(self, ncfile, **kwargs):

        import os
        import pandas as pd
        import numpy as np
        from netCDF4 import Dataset, num2date

        self.fullpath = os.path.abspath(ncfile)

        with Dataset(ncfile, 'r') as D:
            keys = D.variables.keys()
            keys.sort()
            self.varlist = keys

    def print_vars(self, outfile=None):
        """Nicely formatted table of netCDF variables and descriptions"""

        from prettytable import PrettyTable as pT
        from netCDF4 import Dataset

        # open the file for reading
        with Dataset(self.fullpath, 'r') as D:
            # define the columns we want to have, then make the table
            cols = ("Variable", "Long Name", "Units", "Dimensions")
            p = pT(cols)

            # align all columns to the left. easier to read.
            for c in cols:
                p.align[c] = "l"

            # iterate through the keys
            for k in self.varlist:

                long_name, units, dimensions = None, None, None

                if hasattr(D.variables[k], 'long_name'):
                    long_name = getattr(D.variables[k], 'long_name')

                if hasattr(D.variables[k], 'units'):
                    units = getattr(D.variables[k], 'units')

                if hasattr(D.variables[k], 'dimensions'):
                    dimensions = getattr(D.variables[k], 'dimensions')

                # now add the row to the PrettyTable
                p.add_row((k, long_name, units, dimensions))

        # is there an outfile?
        if outfile is not None:
            # if so, open it and write the table to the file
            with open(outfile, 'w') as f:
                f.writelines(p.get_string())
            # and return
            return

        else:
            # otherwise return the PrettyTable back to the user
            print(p)
            return p