import psana
import numpy as np
from tqdm import tqdm
from utils import *
import sys
from pathlib import Path

# run filter threshold
run = sys.argv[1]

if len(sys.argv) == 3:
    fnam, dataset = sys.argv[2].split('.h5')
    fnam = Path(fnam + '.h5')
    print(f'calculating powder for frames with {sys.argv[2]} = True')

    assert(fnam.is_file())
    with h5py.File(fnam) as f:
        filter_bool = f[dataset][()]
        timestamps = f['event_time'][()]

    # make lookup
    filter = {}
    for b, t in zip(filter_bool, timestamps):
        filter[t] = b

    print(list(filter.keys())[:100])
else:
    filter = None

# output file
fnam_out = f'{EXP_FOLDER}/results/h5out/r{run:>04}_powder.h5'

ds = psana.MPIDataSource(f'exp={EXP_NAME}:run={run}:smd')
# for testing
# mpirun -n 2 python powder.py 66
ds.break_after(10000)

env = ds.env() #not sure what this is or why we load it
det = psana.Detector(DET_NAME, env)

smalldata = ds.small_data(fnam_out, keys_to_save=['powder', 'counts'])

counts = 0
powder = np.zeros(DET_SHAPE, dtype=float)

if filter is not None:
    counts_filter = 0
    powder_filter = np.zeros(DET_SHAPE, dtype=float)

if smalldata.master: 
    disable = False
else:
    disable = True

for evt in tqdm(ds.events(), disable=disable):
    frame = photon_convertion(det.calib(evt))

    evtId = evt.get(psana.EventId)
    seconds, nanoseconds = evtId.time()
    t = int((seconds<<32)|nanoseconds)

    # assume same length
    if filter is not None and filter[t]:
        powder_filter += frame
        counts_filter += 1

    counts += 1
    powder += frame


powder = smalldata.sum(powder)
counts = smalldata.sum(counts)

if filter is not None:
    powder_filter = smalldata.sum(powder_filter)
    counts_filter = smalldata.sum(counts_filter)

if smalldata.master:
    powder /= counts

    if filter is not None:
        powder_filter /= counts_filter

smalldata.save({'powder': powder, 'counts': counts})

if filter is not None:
    smalldata.save({'powder_filter': powder_filter, 'counts_filter': counts_filter})

smalldata.close()

