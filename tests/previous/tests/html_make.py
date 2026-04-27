import numpy as np
from mirrordisk import mirrordisk_res_ana
from pathlib import Path

"""
SKIP1 = 3  # Spatial downsample factor in x/y
SKIP2 = 3  # Spectral downsample factor in velocity
VLIM = 2.5  # Velocity limit for masking (|v| < VLIM)
MIN_NPIX = 250  # Minimum voxels for dendrogram structures
NSIGMA = 3
"""

SKIP1 = 3  # Spatial downsample factor in x/y
SKIP2 = 1  # Spectral downsample factor in velocity
VLIM = 2.5  # Velocity limit for masking (|v| < VLIM)
PLOT_LIM = 5  # Plot area in (x,y): (-plot_lim, plot_lim), (-plot_lim, plot_lim)

HTML_DIR = Path("./html")  # Output directory for isosurface HTML

name = "HD163296"
res_fits = Path("/Volumes/T7 Shield/dsharp/mirror/HD163296_CO_res.fits")
params_npy = Path("/Volumes/T7 Shield/dsharp/mirror/HD163296_mirrorparams.npy")

data_r, x_r, vel_r = mirrordisk_res_ana.preprocess(
    name, PLOT_LIM, SKIP1, SKIP2, VLIM, res_fits, params_npy, False
)

# save HTML
X, Y, Z = np.meshgrid(x_r, x_r, vel_r, indexing='ij')
data_convert = data_r.T.astype("float64")
vmin, vmax = np.percentile(data_convert[0], [20, 80])
contour_val = 6.5 * np.std(data_convert[(data_convert > vmin) & (data_convert < vmax)])
print(name, contour_val)
mirrordisk_res_ana.save_isosurface_html(X, Y, Z, data_convert, contour_val, PLOT_LIM, name, HTML_DIR)
