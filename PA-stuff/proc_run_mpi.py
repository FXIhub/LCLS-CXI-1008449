
import time
import numpy as np
import psana

import h5py
import sys

from mpi4py import MPI

from utils import *



t1 =time.time()

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()




run = sys.argv[1]

ds = psana.MPIDataSource(f'exp={EXP_NAME}:run={run}:smd')
#sds.break_after(1000)
det = psana.Detector(DET_NAME)




hist_nbins = 1000
pixel_hist_le30 = np.zeros(hist_nbins)
pixel_hist_ge30 = np.zeros(hist_nbins)


run_mean = np.zeros(DET_SHAPE)
run_meansq = np.zeros(DET_SHAPE)


run_intens = []
timestamps = []

for i, event in enumerate(ds.events()):
    if i%size!=rank: continue # different ranks look at different events

    print(f'Run: {run}, \t event: {i},\t rank:*{rank}', end='\r')
    
    
    calib = det.calib(event)

    run_intens.append(calib.sum())

    run_mean += calib
    run_meansq += calib**2

    hist_le30, hist_bins_le30 = np.histogram(calib[calib<=30], bins=hist_nbins)
    hist_ge30, hist_bins_ge30 = np.histogram(calib[calib>=30], bins=hist_nbins)

    pixel_hist_le30 +=hist_le30
    pixel_hist_ge30 +=hist_ge30

    evtId = event.get(psana.EventId)
    seconds = evtId.time()[0]
    nanoseconds = evtId.time()[1]

    timestamp = seconds+nanoseconds*1e-9

    timestamps.append(timestamp)
    





total_run_intens = comm.gather(run_intens)

total_timestamps = comm.gather(timestamps)

    
total_pixel_hist_le30 = np.empty_like(pixel_hist_le30)
comm.Reduce(pixel_hist_le30, total_pixel_hist_le30)

total_pixel_hist_ge30 = np.empty_like(pixel_hist_ge30)
comm.Reduce(pixel_hist_ge30, total_pixel_hist_ge30)

total_run_mean = np.empty_like(run_mean)
comm.Reduce(run_mean, total_run_mean) # sum the image across all ranks

total_run_meansq= np.empty_like(run_meansq)
comm.Reduce(run_meansq, total_run_meansq) # sum the image across all ranks


MPI.Finalize()


if rank==0:
    t2 = time.time()

    print(f'Completed {i} events in: {np.round(t2-t1)/60} minutes')

    with h5py.File(f'{H5_FOLDER}/r{int(run):04d}_proc.h5', 'w') as f:
        f['/run_mean'] = total_run_mean/i
        f['/run_sigma'] = np.sqrt(total_run_meansq - total_run_mean**2)/i
        
        f['/run_intens']= np.concatenate(total_run_intens[:])
        
        
        f['/pixel_hist_le30'] = total_pixel_hist_le30
        f['/pixel_hist_ge30'] = total_pixel_hist_ge30
        
        f['/pixel_hist_bins_le30'] = hist_bins_le30
        f['/pixel_hist_bins_ge30'] = hist_bins_ge30
        
        f['/timestamps'] = np.concatenate(total_timestamps[:])






