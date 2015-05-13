__author__ = "Jayson Stemmler"

from netCDF4 import Dataset, num2date


class VariableError(Exception):
    pass


class VariableWarning(Warning):
    pass


class netCDF(object):

    def __init__(self, ncfile):

        import os

        assert isinstance(ncfile, str)
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
        :rtype : dict
        """

        # open the file for reading
        with Dataset(self.abspath, 'r') as D:

            variables = dict()

            # iterate through the keys
            for k in self.get_keys():

                long_name, units, dimensions = "None", "None", "None"

                if hasattr(D.variables[k], "long_name"):  # check if it has the 'long_name' attribute
                    long_name = getattr(D.variables[k], "long_name")

                if hasattr(D.variables[k], "units"):      # check if it has the 'units' attribute
                    units = getattr(D.variables[k], "units")

                if hasattr(D.variables[k], "dimensions"): # check if it has the 'dimensions' attribute
                    dimensions = getattr(D.variables[k], "dimensions")

                # save all these attributes into the 'variable' dictionary, keyed on the actual variable name
                variables[k] = dict(long_name=long_name, dimensions=dimensions, units=units)

                # print out the formatted string
                print("{}\n\tlong name: {}\n\tdimensions: {}\n\tunits: {}".
                      format(k, long_name, dimensions, units))

        if return_dict:
            return variables
        else:
            return

    def _parse_variable_list(self, varlist):
        """
        Internal parsing function used to determine the netCDF variables to import.
        :param varlist:
        :return:
        """

        import numpy as np
        import warnings

        # make sure that varlist is of type list, tuple, or string
        assert isinstance(varlist, list) or isinstance(varlist, tuple) or isinstance(varlist, str)

        __keys = self.get_keys()
        _master_list = []

        def _parse_string(ky, s):
            assert isinstance(s, str)

            if s in ky:
                if s not in _master_list:
                    _master_list.append(s)
            elif np.any([s in k for k in ky]):
                [_master_list.append(k) for k in ky if s in k and k not in _master_list]
            else:
                warnings.warn('Warning: {} not found in varlist'.format(s), VariableWarning)

        if isinstance(varlist, str):
            _parse_string(__keys, varlist)

        elif isinstance(varlist, list) or isinstance(varlist, tuple):
            for l in varlist:
                _parse_string(__keys, l)
        else:
            print('UP UP DOWN DOWN LEFT RIGHT LEFT RIGHT B A START')

        if len(_master_list) == 0:
            raise VariableError('Error: No matching variables found')
        else:
            return tuple(_master_list)

    def _check_time_dimension(self, V):

        if hasattr(V, 'dimensions'):
            return True if 'time' in getattr(V, 'dimensions') else False
        else:
            return False

    def get_vars(self, varlist=None):
        if varlist is None:
            raise VariableError('Error: varlist not supplied')

        import pandas as pd
        import numpy as np

        vl = self._parse_variable_list(varlist)

        with Dataset(self.abspath, 'r') as D:
            time_dim = np.array([self._check_time_dimension(D.variables[v]) for v in vl])

            data = dict()

            if 'time' in D.variables.keys() and time_dim.all():
                dt = num2date(D.variables['time'][:], D.variables['time'].units)
                for v in vl:
                    data[v] = D.variables[v][:]

                df = pd.DataFrame(data, index=dt)

                return df
            else:

                for v in vl:
                    data[v] = D.variables[v][:]

                return data