import numpy as np
import h5py
from utils import *  # sorry
import psana

run = 105
cxi_fnam = f'{EXP_FOLDER}/scratch/cxi/r{run:04d}_hits.cxi'

# find events where the low-q signal is 3 sigma 
# above mean
event_times, fiducials = find_hits(run)

ds = psana.DataSource(f'exp={EXP_NAME}:run={run}:idx')
env = ds.env() #not sure what this is or why we load it
det = psana.Detector(DET_NAME, env)

def get_frame_photons(evt):
    frame = photon_convertion(det.calib(evt))
    return frame

xyz, pixel_size = get_xyz(run)


f = h5py.File(cxi_fnam, 'w')


