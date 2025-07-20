
import time
import numpy as np
import psana
from constants import *
import h5py
import sys


from mpi4py import MPI



comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()




run = sys.argv[1]

ds = psana.MPIDataSource(f'exp={EXP_NAME}:run={run}:smd')
#sds.break_after(1000)
det = psana.Detector(DET_NAME)




for i, event in enumerate(ds.events()):
    if i%size!=rank: continue # different ranks look at different events

    print(f'Run: {run}, \t event: {i},\t rank:*{rank}', end='\r')


    evtId = event.get(psana.EventId)
    seconds = evtId.time()[0]
    nanoseconds = evtId.time()[1]
    
    ts = seconds + nanoseconds*1e-9
    timestamps.append(ts)


total_timestamps = comm.gather(timestamps)


MPI.Finalize()


if rank==0:
    with h5py.File(f'{H5_FOLDER}/r{int(run):04d}_proc.h5', 'a') as f:
        #del f['/timestamps']       # load the data
        f['/timestamps'] = np.concatenate(total_timestamps[:])




