import psana
import numpy as np
from tqdm import tqdm
from utils import *
import scipy.constants as sc
import sys

run = sys.argv[1]

# output file
fnam_out = f'{EXP_FOLDER}/results/h5out/r{run:>04}_radial_profiles.h5'


# load geometry
xyz, pixel_size = get_xyz(run)

# load mask
with h5py.File(f'{EXP_FOLDER}/results/mask/combine.h5') as f:
    # reshape to faciltiy standard
    mask = f['data/data'][()].reshape(xyz.shape[1:]) > 0

# load psana data source
ds = psana.MPIDataSource(f'exp={EXP_NAME}:run={run}:smd')
# ds.break_after(100)

env = ds.env() #not sure what this is or why we load it
det = psana.Detector(DET_NAME, env)

smalldata = ds.small_data(fnam_out) #, keys_to_save=['radial_profile', 'r_pixel', 'r_metre', 'q_inv_metre', 'res_metre'])

rad_av = Radial_average(xyz, mask, pixel_size)

if smalldata.master: 
    disable = False
else:
    disable = True

for evt in tqdm(ds.events(), disable=disable):
    frame = photon_convertion(det.calib(evt))
    rav = rad_av.make_rad_av(frame)
    smalldata.event({'radial_profile': rav})

if smalldata.master:
    r_pixel = rad_av.rs / pixel_size
    r_metre = rad_av.rs
    # should probably get this from a datasource
    wav = sc.h * sc.c / (6e3 * sc.e)
    z = xyz[2].ravel()[0]
    r = (r_metre**2 + z**2)**0.5
    q = (r_metre**2 + (z-r_metre)**2)**0.5 / (wav * r)
    res = np.zeros_like(q)
    res[q>0] = 1/q
    res[q==0] = np.inf
else:
    r_pixel = None
    r_metre = None
    q = None
    res = None

smalldata.save({'r_pixel': r_pixel, 'r_metre': r_metre, 'q_inv_metre': q, 'res_metre': res})
smalldata.close()
