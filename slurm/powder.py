import psana
import numpy as np
from tqdm import tqdm
from utils import *
import sys

run = sys.argv[1]

# output file
fnam_out = f'{EXP_FOLDER}/results/h5out/r{run:>04}_powder.h5'

ds = psana.MPIDataSource(f'exp={EXP_NAME}:run={run}:smd')
# for testing
# mpirun -n 2 python powder.py 66
# ds.break_after(100)

env = ds.env() #not sure what this is or why we load it
det = psana.Detector(DET_NAME, env)

smalldata = ds.small_data(fnam_out, keys_to_save=['powder', 'counts'])

counts = 0
powder = np.zeros(DET_SHAPE, dtype=float)

if smalldata.master: 
    disable = False
else:
    disable = True

for evt in tqdm(ds.events(), disable=disable):
    counts += 1
    powder += photon_convertion(det.calib(evt))

powder = smalldata.sum(powder)
counts = smalldata.sum(counts)

if smalldata.master:
    powder /= counts

smalldata.save({'powder': powder, 'counts': counts})
smalldata.close()

