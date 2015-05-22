__author__ = "Jayson Stemmler"

import os
import glob
import warnings
import numpy as np
import pandas as pd
import tables

from netCDF4 import Dataset, num2date

# from ..tools import ProgressBar


class VariableError(Exception):
    """Generic Variable Error exception class"""
    pass


class VariableWarning(Warning):
    """Generic Variable Warning warning class"""
    pass


class NetCDFFolder(object):
    """Sets up the NetCDFFolder class object

    The NetCDFFolder object is a way to manage a folder of netCDF files
    that you may want to ingest into a single analysis. This object allows
    you to define file extensions and patterns in the netCDF filename when
    searching the directory. Additionally, there are several different output
    options for saving your output as a single file.

    Arguments
    -------------------------
        Required:

        -  folder (str)
                the location of the folder on disk. This can be
                relative to the working folder, but absolute paths
                are always better than relative paths.

        Optional:

        -   pat (str)
                a string pattern that you'd like to match for files
                in the directory. Default is None, so that all files that
                match the file extensions will be found.

        -   ext (list, tup)
                valid netCDF file extensions. This defaults
                to 'nc' and 'cdf' which are common netCDF file
                extensions. If you would like to define your own
                list, or have a narrower list, you may modify to
                your liking. This argument can also be a string.

    Raises
    --------------------------

        TypeError: If any of the inputs are not of the correct type.

        IOError: If the folder cannot be found on disk.
    """
    def __init__(self, folder, pat=None, ext=('nc', 'cdf')):

        if not isinstance(folder, str):
            raise TypeError('Folder is not a string')

        if not os.path.isdir(folder):
            raise IOError('Folder {} does not exist on disk'.format(folder))

        self.abspath = os.path.abspath(folder)

        if pat is None:
            filelist = glob.glob(os.path.join(self.abspath, '*'))
            if isinstance(ext, tuple) or isinstance(ext, list):
                to_remove = [i for i in filelist if os.path.basename(i).split('.')[-1] not in ext]
            elif isinstance(ext, str):
                to_remove = [i for i in filelist if os.path.basename(i).split('.')[-1] == ext]
            else:
                raise TypeError('ext is type {}, must be list, tuple, or string'
                                .format(type(ext)))

            for r in to_remove:
                filelist.remove(r)
        else:
            filelist = glob.glob(os.path.join(self.abspath, '*{}*'.format(pat)))

        self.filelist = np.array(filelist, dtype=str)

    def summary(self, detailed=True, **kwargs):
        """Print a summary of the folder contents"""

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

    def process(self, varlist=None, savefile=None, **kwargs):
        """Process each netCDF file using the NetCDFFile class"""

        # allows setting an optional string here for which files to include in analysis.
        # the routine will check to see if 'include' is in the filename.
        include = kwargs.pop('include', None)

        # if you would like to save the output as an hdf5 file, use the
        # keyword "savefile"

        if savefile is not None:
            savefile = os.path.abspath(savefile)
            # check that the save directory exists
            if not os.path.isdir(os.path.split(savefile)[0]):
                raise IOError('Save path "{}" does not exist'.
                              format(os.path.split(savefile)[0]))

        frames = []

        for f in self.filelist:
            if (include is not None) and (not isinstance(include, str)):
                raise TypeError('include is not proper type')

            if (include is None) or (include in f):
                frames.append(NetCDFFile(f).get_vars(varlist=varlist, **kwargs))
            else:
                continue

        # rudimentary way to check if the content of the frames is a pandas object
        # TODO: figure out a better way to check and evaluate this
        is_frame = np.array(['pandas' in str(type(i)) or i is None
                             for i in frames])

        # currently only returns values if everything plays nice with Pandas
        # TODO: make NetCDFFolder.process output allow more output types
        if is_frame.all():
            data = pd.concat(frames)
        else:
            data = None

        if data is not None and savefile is not None:
            try:
                data.to_hdf(savefile, 'data')
            except AttributeError:
                raise Warning("Could not save file")

        return data

class NetCDFFile(object):
    """Sets up the NetCDFFile object class

    Take the netCDF file and add some useful methods to it for easier
    processing and analysis.

    ** NOTE: The scope of this class is still not clearly defined.
             For example, should this include some plotting routines, or
             should it simply be a wrapper for getting variables and information
             out of the netCDF files? I don't know quite yet, so expect this to
             change. Currently it is only a wrapper for the netCDF file
             operations and listing out some variables.

    Arguments
    ---------------------

        Required:

        -   ncfile (str): the full filepath of the netCDF file.
    """

    def __init__(self, ncfile):

        if not isinstance(ncfile, str):
            raise TypeError('ncfile MUST be a string')

        if not os.path.isfile(ncfile):
            raise IOError('ncfile does not exist on disk')

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

                long_name, units, dimensions = "None", "None", "None"

                if hasattr(D.variables[k], "long_name"):  # check if it has the 'long_name' attribute
                    long_name = getattr(D.variables[k], "long_name")

                if hasattr(D.variables[k], "units"):  # check if it has the 'units' attribute
                    units = getattr(D.variables[k], "units")

                if hasattr(D.variables[k], "dimensions"):  # check if it has the 'dimensions' attribute
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

    def _parse_variable_list(self, varlist, exclude, **kwargs):
        """Parse the netCDF variable list"""

        # make sure that varlist is of type list, tuple, or string
        if not isinstance(varlist, (list, tuple, str)):
            raise TypeError("What did you just try and pass? It's not okay.")

        _keys = self.get_keys()
        _master_list = []

        def _parse_string(ky, s, e):
            if not isinstance(s, str):
                raise TypeError("Hey, {} is not a string".format(s))

            if s in ky:
                if s not in _master_list:
                    _master_list.append(s)
            elif np.any([s in k for k in ky]):
                [_master_list.append(k) for k in ky if s in k and k not in _master_list]
            else:
                warnings.warn('Warning: {} not found in varlist'.format(s), VariableWarning)

            return

        if isinstance(varlist, str):
            _parse_string(_keys, varlist, exclude)

        elif isinstance(varlist, (list, tuple)):
            for l in varlist:
                _parse_string(_keys, l, exclude)
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

    def _check_time_dimension(self, v):

        if hasattr(v, 'dimensions'):
            return True if 'time' in getattr(v, 'dimensions') else False
        else:
            return False

    def get_vars(self, varlist=None, exclude=None, **kwargs):
        """Return data from the netCDF file as a Pandas object if possible

        This is the main heavy-lifter of the NetCDFFile class.
        The method parses the variable list passed into it and does
        just about all it can to get you any variables inside the file it
        thinks are matches.

        Requires:
        -  varlist (str, list, tuple)
                can be a single string that you want
                matched to keys in the netCDF variable list.
                If it's not an exact match, it will look for
                partial matches. If list or tuple, they must
                contain all strings. Same rules apply to strings
                inside of lists and tuples.

        Returns:

        -  Pandas DataFrame or dict()
                The output type depends purely on the following conditions:
                  1. 'time' is a netCDF variable
                  2. 'time' exists in the dimensions for each variable
                If both of these conditions are met, it should be able to output
                a pandas DataFrame indexed on a datetime object with the variables
                as the column names. If not, the output is a keyed dictionary with
                the variables as the dictionary keys and the data as a numpy array.
        """

        if varlist is None:
            raise VariableError('Error: varlist not supplied')

        resample = kwargs.pop('resample', None)
        if resample is not None:
            if not isinstance(resample, str):
                raise TypeError("resample must be of type string")

        vl = self._parse_variable_list(varlist, exclude, **kwargs)

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