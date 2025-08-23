import numpy as np
import h5py
from utils import *  # sorry
import psana

run = 105
cxi_fnam = f'{EXP_FOLDER}/scratch/cxi/r{run:04d}_hits.cxi'
mask_fnam = '../mask/combine_r0085.h5'
sample_name = 'Au octahedra'
data_dtype = np.uint8

# find events where the low-q signal is 3 sigma
# above mean
event_times, fiducials, hit_mask = find_hits(run)
event_times = event_times[hit_mask]
fiducials = fiducials[hit_mask]
N = len(event_times)

ds = psana.DataSource(f'exp={EXP_NAME}:run={run}:idx')
env = ds.env() #not sure what this is or why we load it
det = psana.Detector(DET_NAME, env)
myrun = next(ds.runs())

def get_frame_photons(event_time, fiducial):
    et = psana.EventTime(int(event_time),fiducial)
    evt = myrun.event(et)
    frame = photon_convertion(det.calib(evt))
    return frame

xyz, pixel_size = get_xyz(run)
x_pixel_size = y_pixel_size = pixel_size
pixel_area = x_pixel_size * y_pixel_size

with h5py.File(mask_fnam) as f:
    mask = f['data/data'][()]

# -----------------------------
# output:
# -----------------------------
# entry_1/
#   name = "LCLS 2025 cxi100844924 {run}"
#   sample_1/
#       name "{sample_name}"
#   instrument_1
#       detector_1/
#           data
#           good_pixels
#           xyz_map
#           x_pixel_size
#           y_pixel_size
#           pixel_area
#           photon counts
#           lit pixels
#   psana
#       ... stuff from radial_profiles

f = h5py.File(cxi_fnam, 'w')
entry = f.create_group('entry_1')
entry['name'] = f"LCLS 2025 {EXP_NAME} {run}"
entry['sample_1/name'] = f"{sample_name}"
detector = entry.create_group('instrument_1/detector_1')
detector['good_pixels'] = mask
detector['mask'] = mask
detector['x_pixel_size'] = x_pixel_size
detector['y_pixel_size'] = y_pixel_size
detector['pixel_area'] = pixel_area

# get psana stuff from radial profiles
def process_h5_object(name, obj):
    """
    This function is called for each object (group or dataset) in the HDF5 file.
    """
    if isinstance(obj, h5py.Dataset):
        print(f"Found Dataset: {name}")
        if obj.shape[0] == N:
            f[name] = obj[()][hit_mask]

    elif isinstance(obj, h5py.Group):
        print(f"Found Group: {name}")

# Open the HDF5 file
fnam = f'{EXP_FOLDER}/results/h5out/r{run:04d}_radial_profiles.h5'
with h5py.File(fnam, 'r') as g:
    # Use visititems to iterate over all objects and call the processing function
    g.visititems(process_h5_object)


# write data
data = detector_1.create_dataset("data",
            shape=(N,) + DET_SHAPE,
            dtype=data_dtype,
            chunks=(1,) + DET_SHAPE,
            compression='gzip',
            compression_opts=1,
            shuffle=True)

photon_counts = np.zeros((N,), dtype=int)
litpixels = np.zeros((N,), dtype=int)

for i in tqdm(range(len(event_times)), total=N, desc='saving data'):
    frame = get_frame_photons(event_times[i], fiducials[i])
    data[i] = frame
    frame *= mask
    photon_counts[i] = np.sum(frame)
    litpixels[i] = np.sum(frame>0)

# link /entry_1/data_1/data
f["entry_1/data_1/data"] = h5py.SoftLink('/entry_1/instrument_1/detector_1/data')
