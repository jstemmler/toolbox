__author__ = 'Jayson Stemmler'
__created__ = "6/2/15 12:25 PM"

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd

import toolbox as tbx

import seaborn as sns
sns.set_style('darkgrid')

def filled_series(data, points=(5, 95), filled=(25, 75), **kwargs):

    fig = kwargs.pop('fig', None)
    ax = kwargs.pop('ax', None)

    if fig is  None and ax is  None:
        fig, ax = plt.subplots(figsize=(16, 7))
    elif fig is not None and ax is None:
        ax = fig.add_subplot()
    elif fig is None and ax is not None:
        fig = plt.gcf()

    percentile_list = [points[0], filled[0], 50, filled[1], points[1]]

    data_series = (data
                   .groupby(pd.TimeGrouper('1W'))
                   .agg([tbx.tools.percentile(i) for i in percentile_list]))

    strlow = 'pct_{}'.format(points[0])
    strupp = 'pct_{}'.format(points[1])

    lowmid = 'pct_{}'.format(filled[0])
    uppmid = 'pct_{}'.format(filled[1])

    flow = ax.plot_date(data_series.index, data_series[strlow], 'b.')
    fupp = ax.plot_date(data_series.index, data_series[strupp], 'b.')

    [ax.plot([i, i], [l, u], 'k--', zorder=1, linewidth=.3)
        for i, l, u in data_series[[strlow, lowmid]].itertuples()]

    [ax.plot([i, i], [l, u], 'k--', zorder=1, linewidth=.3)
        for i, l, u in data_series[[uppmid, strupp]].itertuples()]

    fl = ax.fill_between(data_series.index,
                         data_series[lowmid],
                         data_series[uppmid],
                         zorder=2, alpha=0.7, color='gray',
                         interpolate=True)

    gray_patch = mpatches.Patch(color='gray')

    med = ax.plot_date(data_series.index, data_series['pct_50'], 'r-', zorder=3)

    l = ax.legend((flow[0], gray_patch, med[0]),
                  ('{}th & {}th percentile'.format(*points),
                   '{}th-{}th percentile'.format(*filled),
                   'Median'))

    fig.autofmt_xdate()

    return fig, ax
