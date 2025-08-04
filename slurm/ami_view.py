import psana
import numpy as np
from tqdm import tqdm
from utils import *
import scipy.constants as sc
import sys

run = sys.argv[1]

# output file
fnam_out = f'{EXP_FOLDER}/results/h5out/r{run:>04}_ami_view.h5'

# load psana data source
ds = psana.MPIDataSource(f'exp={EXP_NAME}:run={run}:smd')
# ds.break_after(100)

env = ds.env() #not sure what this is or why we load it
det = psana.Detector(DET_NAME, env)

smalldata = ds.small_data(fnam_out)

if smalldata.master: 
    disable = False
else:
    disable = True

count = 0
powder = np.zeros(DET_SHAPE, dtype=np.uint32)

for evt in tqdm(ds.events(), disable=disable):
    powder += photon_convertion(det.calib(evt)).astype(powder.dtype)
    count  += 1
    if count == 40:
        smalldata.event({'powder': powder})
        smalldata.event({'count': count})
        powder.fill(0)
        count = 0

if count != 0:
    smalldata.event({'powder': powder})
    smalldata.event({'count': count})

smalldata.save()
smalldata.close()

