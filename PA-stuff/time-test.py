import time
import numpy as np
import psana
from constants import *
import h5py
import sys


from mpi4py import MPI


t1 =time.time()

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
    
    
    calib = det.calib(event)

    if i >200:
        break

t2 = time.time()

print(f'Completed in {t2-t1} seconds')



