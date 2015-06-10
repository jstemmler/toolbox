__author__ = 'Jayson Stemmler'
__created__ = "6/5/15 7:49 AM"

"""
    This set of tools is really just specific to doing some of the
    analysis for the Low CCN project, such as grouping and classifying
    events based on CCN data.

    In addition, there are a couple of plots that are specific to the
    Low CCN stuff, and those will be included here. They leverage the
    plots that can be found in the plotting directory, just with some
    specific settings and colors.
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import timedelta as delt
from .plotting.windrose import windrose
from .plotting.series import filled_series

class LowCCN(object):

    def __init__(self, ccn_data, **kwargs):

        interval = kwargs.pop('interval', '6H')
        how = kwargs.pop('how', 'mean')
        threshold = kwargs.pop('threshold', 20)
        supersat = kwargs.pop('supersaturation', 0.1)
        ccn_var = kwargs.pop('ccn', 'CCN')
        ss_var = kwargs.pop('ss', 'SS')

        self.threshold = threshold
        self.supersaturation = supersat
        self.interval = interval

        try:
            self.ss = ccn_data[ss_var]
            self.ccn = ccn_data[ccn_var]
        except KeyError:
            raise KeyError('Data Keys Not Found')

        self.data = ccn_data
        self.ccn_subset = self.ccn[self.ss == supersat]

        self.resampled = self.ccn_subset.resample(interval, how=how)

        self.low_events = self.resampled[self.resampled <= threshold]

    def summary(self):
        print('First Record: {}'.format(self.ccn.index[0]))
        print('Last Record:  {}'.format(self.ccn.index[-1]))
        print('Total Span:   {}\n'.format(self.ccn.index[-1]-self.ccn.index[0]))

        print(self.data.describe())

        ss_vals = set()
        [ss_vals.add(i) for i in self.ss]
        print("\nUnique SuperSaturation Values:")
        print(sorted(ss_vals))

        print("")

        print("Low-CCN Stats")
        print("\tTotal Number of {} Periods: {}".format(self.interval, len(self.resampled)))
        print("\tNumber of Low-CCN Events: {}".format(len(self.low_events)))

        fig, ax = plt.subplots(figsize=(10, 4))

        n_events = self.low_events.groupby(pd.TimeGrouper('1M')).count()

        ax.bar(n_events.index, n_events.values, width=15, align='center')
        ax.grid('on')
        ax.set_ylabel('Number of Low CCN Events\nPer Month')
        fig.autofmt_xdate()

    def histogram(self, **kwargs):

        fig = kwargs.pop('fig', None)
        ax = kwargs.pop('ax', None)
        figsize = kwargs.pop('figsize', (8, 5))
        ylog = kwargs.pop('ylog', False)

        if fig is None and ax is None:
            fig, ax = plt.subplots(figsize=figsize)

        self.ccn_subset.hist(ax=ax, **kwargs)

        ax.set_title('Histogram of CCN Number Concentration at {}% Supersaturation'
                     .format(self.supersaturation))
        ax.set_xlabel('CCN Number Concentration')
        ax.set_ylabel('Counts')

        if ylog:
            ax.set_yscale('log')
            ax.set_ylim(bottom=0.5)

        return fig, ax

    def series(self, **kwargs):

        fig, ax = filled_series(self.ccn_subset, **kwargs)
        ax.set_ylabel('CCN Number Concentration\n{}% Supersaturation'
                      .format(self.supersaturation))
        ax.grid('on')
        return fig, ax


def group_events(df, low, interval=6):

    def low_ccn_grouper(x, start_times=None, duration=6):
        """ determines whether a timestamp belongs to the
            'low' ccn group or the 'all' ccn group.
            pd.date_range
        """
        if (start_times is None) or (duration is None):
            raise Exception('List of Low CCN Event times and duration not provided')

        if ((x >= start_times) & (x < start_times + delt(hours=duration))).any():
            return 'Low'
        else:
            return 'Non-Low'

    grouped = df.groupby(lambda x:
                         low_ccn_grouper(x,
                                         start_times=low.low_events.index,
                                         duration=interval))

    return grouped

def grouped_rose(group, **kwargs):

    # set up which levels to use as the bins for wind speed
    wind_levels = kwargs.pop('wind_levels', [0, 2, 4, 6, 8, 10, 12])
    figsize = kwargs.pop('figsize', (14, 7))

    deg = kwargs.pop('deg', 'wdir_vec_mean')
    spd = kwargs.pop('spd', 'wspd_vec_mean')

    fig, ax = windrose(direction=group.get_group('Non-Low')[deg],
                       speed=group.get_group('Non-Low')[spd],
                       figsize=figsize, normed=True,
                       bins=wind_levels,
                       rect=[0.05, 0.1, 0.4, 0.8],
                       legend=False)
    ax.set_title('Non-Low CCN Events', y=1.08)

    fig, bx = windrose(direction=group.get_group('Low')[deg],
                       speed=group.get_group('Low')[spd],
                       fig=fig, normed=True,
                       bins=wind_levels,
                       rect=[0.55, 0.1, 0.4, 0.8],
                       legend=False)
    bx.set_title('Low CCN Events', y=1.08)

    bx.legend(fontsize=9, title="Wind Speed Bins (m/s)",
              bbox_to_anchor=[0.5, 0.1], bbox_transform=fig.transFigure,
              loc='lower center', frameon=False)

    return fig

def grouped_box(group, **kwargs):
    """makes a plot based on a pd.Series.groupby object.
    This function will take in a grouped series and make
    a boxplot of each of the groups. Can be as few as 2
    groups, but must be groupby object

    G:  pandas Series groupby object
    ax: the axes to plot into

    returns: ax - the axes handles of the boxplot.
    """

    ax = kwargs.pop('ax', None)

    if ax is None:
        fig, ax = plt.subplots()

    keys = sorted(group.groups.keys())
    nbox = len(keys)

    # look through some kwargs
    whis = kwargs.pop('whis', [5, 95])
    widths = kwargs.pop('widths', 0.75)
    sym = kwargs.pop('sym', '+')

    for i, k in enumerate(keys):
        ax.boxplot(group.get_group(k).dropna(),
                   positions=[i, ],
                   widths=widths,
                   whis=whis,
                   sym=sym)

    ax.set_xticks(np.arange(nbox))
    ax.set_xticklabels(keys)
    ax.set_xlim(left=0-widths, right=i+widths)
    ax.grid('on')
    ax.set_ylabel(group.name)

    return ax
