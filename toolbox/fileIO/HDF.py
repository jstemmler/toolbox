__author__ = 'Jayson Stemmler'
__created__ = "5/22/15 12:04 PM"

import pandas as pd
import os

class read_file(object):
    """ """

    def __init__(self, table, **kwargs):
        """
        :param table: path to .h5 table
        :return: pandas object
        """

        key = kwargs.pop('key', 'data')

        if not isinstance(table, str):
            raise TypeError("HDF5 path must be a string")

        if not os.path.isfile(table):
            raise IOError("File {} could not be found".format(table))

        self.filename = table
        self.key = key

        try:
            self.data = pd.read_hdf(table, key=key)
        except AttributeError:
            self.data = None
