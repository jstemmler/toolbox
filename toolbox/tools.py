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

def percentile(n):
    def percentile_(x):
        return np.percentile(x, n)
    percentile_.__name__ = 'pct_%s' % n
    return percentile_

def uv2deg(u, v):

    def uv2d(u, v):
        d = 270 - (atan2(v, u) * (180/np.pi))
        if d >= 360:
            d = d-360
        if u==0 and v==0:
            d = 0
        return d

    if isinstance(u, float) and isinstance(v, float):
        deg = uv2d(u, v)
    else:
        if len(u) != len(v):
            raise TypeError('U and V must be same length')
        deg = np.array([uv2d(ui, vi) for ui, vi in zip(u, v)])

    return deg

def uv2spd(u, v):
    return np.sqrt((u**2 + v**2))

def uv2met(u, v):

    deg = uv2deg(u, v)
    spd = uv2spd(u, v)

    return deg, spd