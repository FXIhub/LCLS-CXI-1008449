

import numpy as np
import psana
from constants import *
from utils import *
import h5py

import sys


RUN = sys.argv[1]

ds = psana.DataSource(f'exp={EXP_NAME}:run={RUN}:smd')

env = ds.env() #not sure what this is or why we load it

det_name = 'CxiDs1.0:Jungfrau.0' ## or alias 'jungfrau4M'


run_mean = np.zeros(ASSEM_SHAPE)
run_meansq = np.zeros(ASSEM_SHAPE)


det = psana.Detector(det_name, env)

event_inten = []

for i, event in enumerate(ds.events()):
    if i>40:
        break
    print(i, end='\r')
    calib = det.image(event)
    
    run_mean += calib
    run_meansq += calib**2
    event_inten +=[ np.sum(calib)]

run_mean /= i
run_meansq /= i

with h5py.File(f'{H5_FOLDER}/r{RUN}.h5', 'w') as f:
    f['/run_mean'] = run_mean
    f['/run_sigma'] = np.sqrt(run_meansq - run_mean**2)
    f['/event_inten'] = event_inten
    f['/nevents'] = i
    
    
