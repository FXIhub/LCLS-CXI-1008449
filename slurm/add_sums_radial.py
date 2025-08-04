import h5py
import numpy as np
from pathlib import Path
import sys
from utils import *

run = sys.argv[1]

# radial file
fnam = Path(f'{EXP_FOLDER}/results/h5out/r{run:>04}_radial_profiles.h5')

assert(fnam.is_file())

with h5py.File(fnam) as f:
    rads = f['radial_profile'][()]

sums = np.sum(rads[:, :100], axis=1)

with h5py.File(fnam, 'r+') as f:
    key = 'lowq_sum'
    if key in f and f[key].shape == sums.shape:
        f[key][:] = sums
    else:
        if key in f:
            del f[key]
        f[key] = sums
