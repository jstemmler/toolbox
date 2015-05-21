__author__ = 'Jayson Stemmler'
__created__ = "5/14/15 3:37 PM"

import numpy as np
import sys


class ProgressBar(object):
    """Prints a status bar for longer loop operations

    Currently does not work. I will update
    when it actually works properly.
    """

    def __init__(self, **kwargs):

        self._width = kwargs.pop('width', 20)
        self._sym = kwargs.pop('sym', '*')
        self._index = 0
        self._pos = 0

    def start(self, iterable):
        try:
            self._length = len(iterable)
        except TypeError:
            raise TypeError('This object is not iterable')

        sys.stdout.write('|' + ' '*self._width + '|')
        sys.stdout.flush()

    def update(self):

        frac = self._index / self._length
        pos = np.floor(frac * self._width).astype(int)
        sys.stdout.write(str(pos))
        if pos != self._pos:
            pstr = '\r|' + self._sym * pos + ' ' * (self._width - pos) + '|'
            sys.stdout.write(pos)
            sys.stdout.flush()
            self._pos = pos
        self._index += 1

    def finish(self):
        sys.stdout.write('\nProcess Complete\n')
        sys.stdout.flush()
        del self