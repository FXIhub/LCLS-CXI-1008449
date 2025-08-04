

import numpy as np
import psana
import h5py
import matplotlib.pyplot as plt




DET_NAME = 'CxiDs1.0:Jungfrau.0'
DET_SHAPE = (8, 512, 1024)
ASSEM_SHAPE = (2203, 2299)
PIXEL_SIZE = 75e-6

EXP_NAME ='cxi100844924'
EXP_FOLDER = f'/sdf/data/lcls/ds/cxi/{EXP_NAME}'

H5_FOLDER = f'{EXP_FOLDER}/results/h5out'
MASK_FILE =  f'{EXP_FOLDER}/results/mask/combine.h5'
GEOM_FILE = f'{EXP_FOLDER}/results/geom/jul17convert.geom'


def photon_convertion(ar):
    return np.clip((ar/6 + 0.2).astype(int), 0, None)


def get_run_assem_mean(run, suff=''):
    with h5py.File(f'{H5_FOLDER}/r{int(run):04d}_proc{suff}.h5') as f:
        run_mean = f['/run_mean'][:]
    ds = psana.DataSource(f'exp={EXP_NAME}:run={run}:smd')
    det = psana.Detector(DET_NAME)
    for evt in ds.events():
        break
    assem_run_mean = det.image(evt, run_mean)
    return assem_run_mean


def get_run_intens(run, suff=''):
    with h5py.File(f'{H5_FOLDER}/r{int(run):04d}_proc{suff}.h5') as f:
        run_intens = f['/run_intens'][:]
        timestamps = f['/timestamps'][:]

    return timestamps, run_intens


def get_xyz(run, x_offset=0, y_offset=0, detector_distance=0.5709):
    """
    return the x, y and z coordinates for each pixel:
        out.shape = (3, 8, 512, 1024)

    out[0] = x in metres
    out[1] = y in metres
    out[2] = z in metres

    The defaults above are my current best guess.

    The offsets are in pixel units.

    x_offset=36, y_offset=10 for psana geom. 
    But zero for r0115_new.geom, which is refined against
    Siver Behenate runs.
    """
    # ds = psana.DataSource(f'exp={EXP_NAME}:run={run}:smd')
    # env = ds.env() #not sure what this is or why we load it
    # det = psana.Detector(DET_NAME, env)
    # evt = next(ds.events())

    # radial profile
    # x, y, z = det.coords_xyz(run)
    # pixel_size = 1e-6 * det.pixel_size(evt)
    # xyz = 1e-6 * np.array([x, y, z])
    x, y = get_xy_map()[:2]

    xyz = np.empty((3,) + x.shape, x.dtype)
    xyz[0] = x
    xyz[1] = y

    # offset
    xyz[0] += x_offset * PIXEL_SIZE
    xyz[1] += y_offset * PIXEL_SIZE

    # set detector distance
    xyz[2] = detector_distance
    return xyz, PIXEL_SIZE


def pixel_maps_from_geometry_file(fnam, return_dict = False):
    """
    Return pixel and radius maps from the geometry file

    Input: geometry filename

    Output: x: slab-like pixel map with x coordinate of each slab pixel in the reference system of the detector
            y: slab-like pixel map with y coordinate of each slab pixel in the reference system of the detector
            z: slab-like pixel map with distance of each pixel from the center of the reference system.

    Note:
            ss || y
            fs || x

            vectors should be given by [x, y]
    """
    f = open(fnam, 'r')
    f_lines = []
    for line in f:
        f_lines.append(line)

    keyword_list = ['min_fs', 'min_ss', 'max_fs', 'max_ss', 'fs', 'ss', 'corner_x', 'corner_y']

    detector_dict = {}

    panel_lines = [ x for x in f_lines if '/' in x and 'bad' not in x and not x.startswith(";")]


    for pline in panel_lines:
        items = pline.split('=')[0].split('/')
        if len(items) == 2 :
            panel = items[0].strip()
            property = items[1].strip()
            if property in keyword_list:
                if panel not in detector_dict.keys():
                    detector_dict[panel] = {}
                detector_dict[panel][property] = pline.split('=')[1].split(';')[0].strip()

    parsed_detector_dict = {}

    for p in detector_dict.keys():
        parsed_detector_dict[p] = {}
        parsed_detector_dict[p]['min_fs'] = int( float(detector_dict[p]['min_fs'] ))
        parsed_detector_dict[p]['max_fs'] = int( float(detector_dict[p]['max_fs'] ))
        parsed_detector_dict[p]['min_ss'] = int( float(detector_dict[p]['min_ss'] ))
        parsed_detector_dict[p]['max_ss'] = int( float(detector_dict[p]['max_ss'] ))
        parsed_detector_dict[p]['fs'] = []
        parsed_detector_dict[p]['fs'].append( float( detector_dict[p]['fs'].split('x')[0] ) )
        parsed_detector_dict[p]['fs'].append( float( detector_dict[p]['fs'].split('x')[1].split('y')[0] ) )
        parsed_detector_dict[p]['ss'] = []
        parsed_detector_dict[p]['ss'].append( float( detector_dict[p]['ss'].split('x')[0] ) )
        parsed_detector_dict[p]['ss'].append( float( detector_dict[p]['ss'].split('x')[1].split('y')[0] ) )

        parsed_detector_dict[p]['corner_x'] = float( detector_dict[p]['corner_x'] )
        parsed_detector_dict[p]['corner_y'] = float( detector_dict[p]['corner_y'] )

    max_slab_fs = np.array([parsed_detector_dict[k]['max_fs'] for k in parsed_detector_dict.keys()]).max()
    max_slab_ss = np.array([parsed_detector_dict[k]['max_ss'] for k in parsed_detector_dict.keys()]).max()

    x = np.zeros((max_slab_ss+1, max_slab_fs+1), dtype=np.float32)
    y = np.zeros((max_slab_ss+1, max_slab_fs+1), dtype=np.float32)

    for p in parsed_detector_dict.keys():
        # get the pixel coords for this asic
        i, j = np.meshgrid( np.arange(parsed_detector_dict[p]['max_ss'] - parsed_detector_dict[p]['min_ss'] + 1),
                               np.arange(parsed_detector_dict[p]['max_fs'] - parsed_detector_dict[p]['min_fs'] + 1), indexing='ij')

        #
        # make the y-x ( ss, fs ) vectors, using complex notation
        dx  = parsed_detector_dict[p]['fs'][1] + 1J * parsed_detector_dict[p]['fs'][0]
        dy  = parsed_detector_dict[p]['ss'][1] + 1J * parsed_detector_dict[p]['ss'][0]
        r_0 = parsed_detector_dict[p]['corner_y'] + 1J * parsed_detector_dict[p]['corner_x']
        #
        r   = i * dy + j * dx + r_0
        #
        y[parsed_detector_dict[p]['min_ss']: parsed_detector_dict[p]['max_ss'] + 1, parsed_detector_dict[p]['min_fs']: parsed_detector_dict[p]['max_fs'] + 1] = r.real
        x[parsed_detector_dict[p]['min_ss']: parsed_detector_dict[p]['max_ss'] + 1, parsed_detector_dict[p]['min_fs']: parsed_detector_dict[p]['max_fs'] + 1] = r.imag

    if return_dict :
        return x, y, parsed_detector_dict
    else :
        return x, y


def get_xy_map(
        geom_fnam='/sdf/data/lcls/ds/cxi/cxi100844924/scratch/LCLS-CXI-1008449/geom/r0115_new.geom',
        slab_shape=False
        ):
    # pixel size 75e-6 m
    x, y, parsed_detector_dict = pixel_maps_from_geometry_file(geom_fnam, return_dict=True)

    # make panel map
    panel_id = -np.ones(x.shape, dtype=int)
    panel_index_to_name = {}
    index = 0
    for name, panel in parsed_detector_dict.items():
        ss0 = panel['min_ss']
        ss1 = panel['max_ss']+1
        fs0 = panel['min_fs']
        fs1 = panel['max_fs']+1
        panel_id[ss0:ss1, fs0:fs1] = index
        panel_index_to_name[index] = name
        index += 1

    x *= PIXEL_SIZE
    y *= PIXEL_SIZE

    if not slab_shape:
        x = x.reshape(DET_SHAPE)
        y = y.reshape(DET_SHAPE)

    # this is in pixel units
    # xyz = np.zeros((16448, 1030), dtype=float)
    return x, y, panel_id, panel_index_to_name, parsed_detector_dict


def geom_cor(arr):
    x, y = get_xy_map()[:2]
    x0, y0 = x.min(), y.min()
    x = np.round(x-x0).astype(int)
    y = np.round(y-y0).astype(int)
    M = y.max() + 1
    N = x.max() + 1
    out = np.empty((M, N), dtype=arr.dtype)
    out.fill(np.nan)
    out[y, x] = arr
    return out, (y0, x0)

class Geom_cor():

    def __init__(self, dtype):
        x, y = get_xy_map()[:2]
        x0, y0 = x.min(), y.min()
        x -= x0
        y -= y0
        self.x = np.round(x).astype(np.uint16)
        self.y = np.round(y).astype(np.uint16)
        M = int(y.max() + 2)
        N = int(x.max() + 2)
        self.out = np.empty((M, N), dtype=dtype)
        self.out.fill(np.nan)
        self.centre = (y0, x0)

    def get(self, arr):
        self.out[self.y, self.x] = arr
        return self.out


class Radial_average():
    """
    A class for doing radial averages, faster than calling a function for repeated calls
    """

    def __init__(self, xyz, mask, radial_bin_size, min_rad=None, max_rad=None):
        self.r = (xyz[0]**2 + xyz[1]**2)**0.5
        self.radial_bin_size = radial_bin_size

        self.mask = mask.copy()
        if min_rad:
            self.mask[self.r < min_rad] = False
        if max_rad:
            self.mask[self.r > max_rad] = False

        # integer label for radial bin
        self.rl = np.rint(self.r[self.mask] / radial_bin_size).astype(int).ravel()

        # just to speed things up a little
        self.rl = np.ascontiguousarray(self.rl)

        # number of pixels contributing to each bin
        self.rcounts = np.bincount(self.rl.ravel())

        # for reference
        self.rs = np.arange(np.max(self.rl)+1) * self.radial_bin_size

    def make_rad_av(self, ar):
        rsum = np.bincount(self.rl, ar[self.mask])

        # normalise, might not want to do this
        rsum /= np.clip(self.rcounts, 1e-20, None)
        return rsum

    def make_im(self, rav):
        im = np.zeros(self.r.shape, dtype = rav.dtype)
        im[self.mask] = rav[self.rl]
        return im


def get_run_azimuthal_average(run, rbins=100, rmin=None, rmax=None, suff=''):

    with h5py.File(f'{H5_FOLDER}/r{int(run):04d}_proc{suff}.h5') as f:
        run_mean = f['/run_mean'][:]
    
    ds = psana.DataSource(f'exp={EXP_NAME}:run={run}:smd')
    det = psana.Detector(DET_NAME)
    
    cx, cy = det.coords_xy(run)
    
    
    r = np.sqrt(cx**2+cy**2)

    if rmin is None:
        rmin=r.min()
    if rmax is None:
        rmax = r.max()
    
    
    rbins = np.linspace(rmin, rmax, rbins)
    r_digit = np.digitize(r, rbins)
    
    r_counts = np.bincount(r_digit.flatten())
    
    r_sum = np.bincount(r_digit.flatten(), weights=run_mean.flatten())
    
    r_sum[r_counts>0] /= r_counts[r_counts>0]

    return rbins, r_sum


def assem_plot_zoom():
    plt.xlim([500,1800])
    plt.ylim([450,1750])

