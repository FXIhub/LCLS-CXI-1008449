

import numpy as np
import psana
from constants import *
from utils import *
import h5py

import sys
import time
print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')



RUN = sys.argv[1]

ds = psana.DataSource(f'exp={EXP_NAME}:run={RUN}:smd')

env = ds.env() #not sure what this is or why we load it

det_name = 'CxiDs1.0:Jungfrau.0' ## or alias 'jungfrau4M'



hist_nbins = 1000
pixel_hist_le25 = np.zeros(hist_nbins)
pixel_hist_ge25 = np.zeros(hist_nbins)





det = psana.Detector(det_name, env)





x = DET_SHAPE
y = det.calib


run_mean = np.zeros(x)
run_meansq = np.zeros(x)
event_inten = []
t1 = time.time()

for i, event in enumerate(ds.events()):

    #if i>20:
    #    break
  
   
    print(f'Run: {RUN}, \t event: {i}', end='\r')
    
    
    calib = y(event)

    run_mean += calib
    run_meansq += calib**2
    event_inten +=[ np.sum(calib) ]
    
    hist, pixel_hist_bins_le25 = np.histogram(calib[calib<=25], bins=hist_nbins)
    pixel_hist_le25 +=hist

    
    hist, pixel_hist_bins_ge25 = np.histogram(calib[calib>=25], bins=hist_nbins)
    pixel_hist_ge25 +=hist
print('######################################################')
print('######################################################')


run_mean /= i
run_meansq /= i

with h5py.File(f'{H5_FOLDER}/r{RUN}.h5', 'w') as f:
    f['/run_mean'] = run_mean
    f['/run_sigma'] = np.sqrt(run_meansq - run_mean**2)
    f['/event_inten'] = event_inten
    f['/nevents'] = i
    f['/pixel_hist_le25'] = pixel_hist_le25
    f['/pixel_hist_bins_le25'] = pixel_hist_bins_le25
    f['/pixel_hist_ge25'] = pixel_hist_ge25
    f['/pixel_hist_bins_ge25'] = pixel_hist_bins_ge25

t2 = time.time()

print(f'Time to complete: {np.round(t2-t1)/60} minutes')
    
    
    
