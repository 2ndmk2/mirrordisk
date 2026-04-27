import numpy as np
from mirrordisk import mirror
import importlib
import os
import pandas as pd
import time
import psutil
import glob 


folder_to_mirror = "/Volumes/T7 Shield/dsharp/mirror/"
original_fits ="/Volumes/T7 Shield/dsharp/data/HD163296_CO.fits"
pa_rad_initial = 142 * np.pi/180.0 ## radian
x_cen_initial = 0 ## arcsec
param_path = "/Volumes/T7 Shield/dsharp/mirror/HD163296_mirrorparams" 
mirror.process_fits_file(original_fits, folder_to_mirror,  param_path, vsys_init =None,pa_init=pa_rad_initial , x_cen_init =0,  inp_max = 6.0, n_points = 120, vec_offsets = np.array([-1.4, -1.2, -1.0, -0.8, -0.6, -0.4, -0.2]) )

