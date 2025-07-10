

import numpy as np
import psana
from constants import *




def get_ds(run_number):
    return psana.DataSource(f'exp={EXP_NAME}:run={run_number}:smd')


def get_det(run_number):
    ds = get_ds(run_number)
    env = ds.env()
    return psana.Detector(DET_NAME, env)






