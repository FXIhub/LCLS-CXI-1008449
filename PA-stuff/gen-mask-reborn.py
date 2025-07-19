from reborn import detector

from constants import EXP_FOLDER, DET_SHAPE
import h5py
import numpy as np


m1 = detector.load_pad_masks(f'{EXP_FOLDER}/results/mask/edge_mask.mask')
m2 = detector.load_pad_masks(f'{EXP_FOLDER}/results/mask/probably_dead_minmax_run22.mask')

with h5py.File(f'{EXP_FOLDER}/results/mask/run32_mask.h5') as f:
    m3 = f['/data/data'][:]


m1 = np.array(m1).flatten()
m2 = np.array(m2).flatten()
m3 = np.array(m3).flatten()

combine_m = m1*m2*m3

combine_m = combine_m.reshape((4096, 1024))

#print(m1.max())

#print(m1.shape)
#print(m2.shape)

#combine_m = m1+m2
#combine_m = np.array(combine_m).reshape((4096, 1024))
with h5py.File(f'{EXP_FOLDER}/results/mask/combine.h5', 'w') as f:
    f['/data/data'] = combine_m


