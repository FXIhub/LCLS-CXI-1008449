import h5py
import numpy as np
import scipy.constants as sc
from tqdm import tqdm
from utils import *  # sorry

def add_f(f, key, value):
    if key in f and f[key].shape == value.shape and f[key].dtype == value.dtype:
        f[key][:] = value
        return
    elif key in f:
        del f[key]

    f[key] = value

run = 105
cxi_fnam = f'{EXP_FOLDER}/scratch/cxi/r{run:04d}_hits.cxi'

f = h5py.File(cxi_fnam, 'r+')

# should get this from a data source
wav = sc.h * sc.c / (6e3 * sc.e)
N = f['entry_1/data_1/data'].shape[0]
wav = wav * np.ones((N,), dtype=float)
add_f(f, '/entry_1/instrument_1/source_1/photon_wavelength', wav)

detector = f['entry_1/instrument_1/detector_1']

# change mask (should make better one)
# mask_fnam = '../mask/psana_mask.py'
# with h5py.File(mask_fnam) as g:
#     mask = g['data/data'][()]

# add geometry (shouldn't need this anymore)
"""
xyz, pixel_size = get_xyz(run)
add_f(detector, 'xyz_map', xyz)
"""

# add photon counts (shouldn't need this anymore)
"""
mask = detector['mask'][()]
data = detector['data']

N = data.shape[0]

photon_counts = np.zeros((N,), dtype=int)
litpixels = np.zeros((N,), dtype=int)
for d in tqdm(range(data.shape[0])):
    frame = data[d]
    frame *= mask
    photon_counts[d] = np.sum(frame)
    litpixels[d] = np.sum(frame>0)

add_f(detector, 'photon_counts', photon_counts)
add_f(detector, 'litpixels', litpixels)
"""


