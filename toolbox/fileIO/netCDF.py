__author__ = "Jayson Stemmler"

from netCDF4 import Dataset, num2date


class VariableError(Exception):
    pass


class VariableWarning(Warning):
    pass


class NetCDFFolder(object):

    def __init__(self, folder, pat=None, ext=('nc', 'cdf')):

        import os
        import glob
        import numpy as np

        assert isinstance(folder, str)
        assert os.path.isdir(folder)

        self.abspath = os.path.abspath(folder)

        if pat is None:
            filelist = glob.glob(os.path.join(self.abspath, '*'))
            to_remove = [i for i in filelist if os.path.basename(i).split('.')[-1] not in ext]
            for r in to_remove:
                filelist.remove(r)
        else:
            filelist = glob.glob(os.path.join(self.abspath, pat))

        self.filelist = np.array(filelist, dtype=str)

    def summary(self, detailed=True, **kwargs):

        import os

        print(self.abspath)
        print("Found {} files total\n".format(len(self.filelist)))

        if detailed:
            streams = dict()
            sep = kwargs.pop('sep', '.')

            for f in self.filelist:
                bn = os.path.basename(f).split(sep)[0]
                if bn in streams.keys():
                    streams[bn] += 1
                else:
                    streams[bn] = 1

            for k, v in streams.iteritems():
                print("Found {} items for datastream {}".format(v, k))

    def process(self, varlist=None, **kwargs):

        import pandas as pd
        import numpy as np

        include = kwargs.pop('include', None)

        if include:
            frames = [NetCDFFile(f).get_vars(varlist=varlist, **kwargs)
                      for f in self.filelist
                      if include in f]
        else:
            frames = [NetCDFFile(f).get_vars(varlist=varlist, **kwargs)
                      for f in self.filelist]

        is_frame = np.array(['pandas' in str(type(i)) or i is None
                             for i in frames])

        if is_frame.all():
            return pd.concat(frames)
        else:
            return None


class NetCDFFile(object):

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

    def _parse_variable_list(self, varlist, **kwargs):
        """
        Internal parsing function used to determine the netCDF variables to import.
        :param varlist:
        :return:
        """

        import numpy as np
        import warnings

        # make sure that varlist is of type list, tuple, or string
        assert isinstance(varlist, (list, tuple, str))

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

        elif isinstance(varlist, (list, tuple)):
            for l in varlist:
                _parse_string(__keys, l)
        else:
            print('UP UP DOWN DOWN LEFT RIGHT LEFT RIGHT B A START')

        ignore_empty = kwargs.pop('ignore_empty', False)

        if len(_master_list) == 0:
            if ignore_empty:
                return None
            else:
                raise VariableError('Error: No matching variables found')
        else:
            return tuple(_master_list)

    def _check_time_dimension(self, V):

        if hasattr(V, 'dimensions'):
            return True if 'time' in getattr(V, 'dimensions') else False
        else:
            return False

    def get_vars(self, varlist=None, **kwargs):

        if varlist is None:
            raise VariableError('Error: varlist not supplied')

        import pandas as pd
        import numpy as np

        resample = kwargs.pop('resample', None)
        assert isinstance(resample, str)

        vl = self._parse_variable_list(varlist, **kwargs)

        if vl is None:
            return None

        with Dataset(self.abspath, 'r') as D:
            time_dim = np.array([self._check_time_dimension(D.variables[v]) for v in vl])

            data = dict()

            if 'time' in D.variables.keys() and time_dim.all():
                dt = num2date(D.variables['time'][:], D.variables['time'].units)
                for v in vl:
                    data[v] = D.variables[v][:]

                if resample is None:
                    df = pd.DataFrame(data, index=dt)
                else:
                    df = pd.DataFrame(data, index=dt).resample(resample)

                return df
            else:

                for v in vl:
                    data[v] = D.variables[v][:]

                return data