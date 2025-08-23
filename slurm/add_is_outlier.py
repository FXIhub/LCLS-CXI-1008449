import h5py
import numpy as np
from scipy import optimize
from pathlib import Path
import sys
from utils import *

run = sys.argv[1]
rmin = 100
rmax = 200
sigma_min = -4
sigma_max = 4

# radial file
fnam = Path(f'{EXP_FOLDER}/results/h5out/r{run:>04}_radial_profiles.h5')

assert(fnam.is_file())

with h5py.File(fnam) as f:
    rsums = np.sum(f['radial_sums'][:, rmin:rmax], axis=1)

# fit gaussian
def gaussian(x, a, x0, sigma):
    return a * np.exp(-(x-x0)**2 / 2 / sigma**2)

h = np.bincount(rsums.astype(int))
x = np.arange(len(h))
x0 = np.argmax(h)
a = h[x0]
sigma = 100

popt, pcov = optimize.curve_fit(gaussian,
                                x, h,
                                p0=(a, x0, sigma))

s = (rsums - popt[1]) / popt[2]
mask = (s > sigma_min) * (s < sigma_max)

out = {
        'lowq_sum': rsums, 
        'lowq_sum_sigma': popt[2],
        'lowq_sum_mean': popt[1],
        'lowq_sum_amplitude': popt[0],
        'is_not_outlier': mask
      }

with h5py.File(fnam, 'r+') as f:
    key = 'lowq_sum'
    for key, value in out.items():
        if key in f:
            try:
                f[key][:] = value
            except:
                del f[key]
        else:
            f[key] = value

