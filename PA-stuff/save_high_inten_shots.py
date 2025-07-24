
import time
import numpy as np
import psana
import h5py
import sys

from utils import *

from mpi4py import MPI


t1 =time.time()

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()



run = sys.argv[1]


timestamps, run_intens = get_run_intens(run)
med = np.median(run_intens)
    
loc = np.where(run_intens < 10*med)
timestamps, run_intens = timestamps[loc], run_intens[loc]

loc = np.where(run_intens > med/10)
timestamps, run_intens = timestamps[loc], run_intens[loc]

p16 = np.percentile(run_intens, 16)
p84 = np.percentile(run_intens, 84)
wid = p84 - p16

ds = psana.MPIDataSource(f'exp={EXP_NAME}:run={run}:smd')
det = psana.Detector(DET_NAME)




shots = []
timestamps = []

for i, event in enumerate(ds.events()):
    if i%size!=rank: continue # different ranks look at different events

    print(f'Run: {run}, \t event: {i},\t rank:*{rank}', end='\r')
    
    
    calib = det.calib(event)

    intens = calib.sum()

    if intens>med+wid:
        
        shots.append(calib)
    
        evtId = event.get(psana.EventId)
        seconds = evtId.time()[0]
        nanoseconds = evtId.time()[1]
    
        timestamp = seconds+nanoseconds*1e-9
    
        timestamps.append(timestamp)
    

total_shots = comm.gather(shots)

total_timestamps = comm.gather(timestamps)

MPI.Finalize()


if rank==0:
    t2 = time.time()

    print(f'Completed {i} events in: {np.round(t2-t1)/60} minutes')

    with h5py.File(f'{H5_FOLDER}/r{int(run):04d}_high_intens_shots.h5', 'w') as f:
        f['/shots'] = np.concatenate(total_shots[:])
        f['/timestamps'] = np.concatenate(total_timestamps[:])






