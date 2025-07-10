

from utils import *
from constants import *


ds = get_ds(9)
det = get_det(9)

for event in ds.events():
    x = det.calib(event)
    break

print(x.shape)
    


