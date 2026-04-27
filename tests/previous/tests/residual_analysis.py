import numpy as np
from mirrordisk import mirrordisk_res_ana
import pandas as pd
from pathlib import Path


SKIP1 = 1  # Spatial downsample factor in x/y
SKIP2 = 1  # Spectral downsample factor in velocity
VLIM = 2.5  # Velocity limit for masking (|v| < VLIM). Compute momentum maps within vsys - VLIM <  v < vsys + VLIM
MIN_NPIX = 1000  # Minimum voxels for dendrogram structures
NSIGMA = 5 # Intensity threshold for dendrogram structures (NSIGMA*sigma)
PLOT_LIM = 5 # Plot area in (x,y): (-plot_lim, plot_lim),  (-plot_lim, plot_lim)
OUT_DIR = Path("./moms")  # Output directory for moment maps
HTML_DIR = Path("./html")  # Output directory for isosurface HTML


name ="HD163296"
res_fits = "/Volumes/T7 Shield/dsharp/mirror/HD163296_CO_res.fits"
params_npy = "/Volumes/T7 Shield/dsharp/mirror/HD163296_mirrorparams.npy"

## Preprocessing
data_r, x_r, vel_r = mirrordisk_res_ana.preprocess(name, PLOT_LIM, SKIP1, SKIP2, VLIM, res_fits,params_npy, False)

#### Moments for positive
mask = mirrordisk_res_ana.compute_dendro_mask(data_r,NSIGMA, MIN_NPIX)
masked_data = np.where(mask, data_r, np.nan)
m0, m1 = mirrordisk_res_ana.compute_moments(masked_data, vel_r)
mirrordisk_res_ana.plot_moments(m0, m1, x_r, name, OUT_DIR, True)
m8 = mirrordisk_res_ana.compute_moment_n(masked_data, vel_r, 8)
m9 = mirrordisk_res_ana.compute_moment_n(masked_data, vel_r, 9)
mirrordisk_res_ana.plot_scalar_map(m8, x_r, f"{name}_pos", OUT_DIR, "Moment8")
mirrordisk_res_ana.plot_scalar_map(m9, x_r, f"{name}_pos", OUT_DIR, "Moment9", cmap='bwr', symmetric=True)

#### Moments for negative
mask = mirrordisk_res_ana.compute_dendro_mask(-data_r,NSIGMA, MIN_NPIX)
masked_data = np.where(mask, -data_r, np.nan)
m0, m1 = mirrordisk_res_ana.compute_moments(masked_data, vel_r)
mirrordisk_res_ana.plot_moments(m0, m1, x_r, name, OUT_DIR, False)
m8 = mirrordisk_res_ana.compute_moment_n(masked_data, vel_r, 8)
m9 = mirrordisk_res_ana.compute_moment_n(masked_data, vel_r, 9)
mirrordisk_res_ana.plot_scalar_map(m8, x_r, f"{name}_neg", OUT_DIR, "Moment8")
mirrordisk_res_ana.plot_scalar_map(m9, x_r, f"{name}_neg", OUT_DIR, "Moment9", cmap='bwr', symmetric=True)
