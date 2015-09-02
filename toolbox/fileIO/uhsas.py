from __future__ import division

__author__ = 'Jayson Stemmler'
__created__ = "8/17/15 8:10 AM"

import os

from netCDF4 import Dataset, num2date
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np

class UHSAS(object):

    def __init__(self, filepath):

        if not isinstance(filepath, str):
            raise TypeError("'filepath' must be a string")

        uhsas_file = os.path.abspath(filepath)

        with Dataset(uhsas_file, 'r') as F:

            self.datetimes = num2date(F.variables['time'][:], F.variables['time'].units)
            self.hour = np.array([d.hour for d in self.datetimes])

            self.size_distribution = F.variables['size_distribution'][:]
            self.total_concentration = ((self.size_distribution.sum(axis=1)) /
                                        ((F.variables['sampling_volume'][:] / 60) * 10))
            self.sampling_volume = F.variables['sampling_volume'][:]
            self.lower_size_limit = F.variables['lower_size_limit'][:]
            self.upper_size_limit = F.variables['upper_size_limit'][:]

            self.time = F.variables['time'][:]

    def concentration(self, llim, sample_rate=10):

        mask = self.lower_size_limit >= llim
        masked_dist = self.size_distribution[:, mask]

        return masked_dist.sum(axis=1) / ((self.sampling_volume / 60) * sample_rate)

    def plot(self, savefile=None, **kwargs):

        fig = plt.figure(figsize=(12, 7))

        ax = fig.add_axes([0.07, 0.33, 0.83, 0.6])

        cmap = kwargs.pop("cmap", cm.Spectral_r)
        vmin = kwargs.pop("vmin", 0)
        vmax = kwargs.pop("vmax", np.percentile(self.size_distribution, 99))

        image = ax.pcolormesh(self.datetimes,
                              np.array(self.lower_size_limit.tolist()+[self.upper_size_limit[-1]]),
                              self.size_distribution.T,
                              vmin=vmin,
                              vmax=vmax,
                              cmap=cmap,
                              **kwargs)
        ax.set_yscale('log')
        # image = ax.imshow(self.size_distribution,
        #                   aspect='auto',
        #                   interpolation='none',
        #                   extent=(self.lower_size_limit[0], self.upper_size_limit[-1],
        #                           np.ceil(self.hour[-1]), np.floor(self.hour[0])),
        #                   vmin=0,
        #                   vmax=np.percentile(self.size_distribution, 99.9))

        cbax = fig.add_axes([0.92, 0.33, 0.02, 0.6])
        cbar = fig.colorbar(image, cax=cbax)
        cbar.set_label('Count')

        ax.set_xticklabels('')
        ax.set_ylabel("Size Bin")

        #ytk = ax.get_yticks()
        #ytk = [self.lower_size_limit[0]] + ytk.tolist()
        #ax.set_yticks(ytk)
        ax.set_yticks((self.lower_size_limit[0], 100, 200, 300, 400, 500, 700, 1000))
        ax.set_yticklabels([str(int(i)) for i in ax.get_yticks()])

        ax.set_ylim(bottom=self.lower_size_limit[0],
                    top=self.upper_size_limit[-1])

        ax.set_title("UHSAS Particle Size Distribution\n{}-{:02}-{:02}"
                     .format(self.datetimes[0].year,
                             self.datetimes[0].month,
                             self.datetimes[0].day))

        ax2 = fig.add_axes([0.07, 0.1, 0.83, 0.2])

        line = ax2.plot(self.datetimes, self.total_concentration, 'k-')
        ax2.grid('on')
        ax2.set_ylabel('Total Concentration')

        ax2.set_xlabel("Date/Time")

        if savefile is not None:
            if not isinstance(savefile, str):
                raise TypeError("'savefile' path must be a string")

            directory, filename = os.path.split(savefile)

            if not os.path.isdir(directory):
                os.makedirs(directory)

            if not filename:
                fdate = self.datetimes[0]
                filename = 'uhsas_{}-{:02}-{:02}.png'.format(fdate.year, fdate.month, fdate.day)

            fig.savefig(os.path.join(directory, filename), dpi=300)

        return fig, (ax, ax2)


if __name__ == "__main__":

    file = '/Volumes/NiftyDrive/Research/data/ENA/uhsas/aos/enaaosuhsasC1.a1.20140315.000006.cdf'
    if not os.path.isfile(file):
        raise IOError('File Does Not Exist')

    U = UHSAS(file)
    U.plot(savefile='./')

    pass
