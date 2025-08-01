

import numpy as np
import psana
import h5py
import matplotlib.pyplot as plt




DET_NAME = 'CxiDs1.0:Jungfrau.0'
DET_SHAPE = (8, 512, 1024)
ASSEM_SHAPE = (2203, 2299)

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

