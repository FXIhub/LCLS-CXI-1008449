

import numpy as np
import psana
from constants import *
import h5py
import matplotlib.pyplot as plt


def get_run_assem_mean(run, sf=1):
    with h5py.File(f'{H5_FOLDER}/r{int(run):04d}_proc.h5') as f:
        run_mean = f['/run_mean'][:]
    ds = psana.DataSource(f'exp={EXP_NAME}:run={run}:smd')
    det = psana.Detector(DET_NAME)
    for evt in ds.events():
        break
    assem_run_mean = det.image(evt, run_mean)*sf
    return assem_run_mean

def get_run_assem_intens_filt_mean(run, sf=1):
    with h5py.File(f'{H5_FOLDER}/intens_filt/r{int(run):04d}_proc_intens_filt.h5') as f:
        run_mean = f['/run_mean'][:]
    ds = psana.DataSource(f'exp={EXP_NAME}:run={run}:smd')
    det = psana.Detector(DET_NAME)
    for evt in ds.events():
        break
    assem_run_mean = det.image(evt, run_mean)*sf
    return assem_run_mean

def get_run_assem_high_intens_filt_mean(run, sf=1):
    with h5py.File(f'{H5_FOLDER}/intens_filt/r{int(run):04d}_proc_high_intens_filt.h5') as f:
        run_mean = f['/run_mean'][:]
    ds = psana.DataSource(f'exp={EXP_NAME}:run={run}:smd')
    det = psana.Detector(DET_NAME)
    for evt in ds.events():
        break
    assem_run_mean = det.image(evt, run_mean)*sf
    return assem_run_mean

def get_run_intens(run):
    with h5py.File(f'{H5_FOLDER}/r{int(run):04d}_proc.h5') as f:
        run_intens = f['/run_intens'][:]
        timestamps = f['/timestamps'][:]

    return timestamps, run_intens


def get_run_azimuthal_average(run, rbins=100, rmin=None, rmax=None, sf=1):

    with h5py.File(f'{H5_FOLDER}/r{int(run):04d}_proc.h5') as f:
        run_mean = f['/run_mean'][:]*sf
    
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

