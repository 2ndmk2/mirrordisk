import os
import time
import numpy as np
import psutil
from astropy.io import fits
from mirrordisk import mirrordisk_make, mirrordisk_optimize

def process_fits_file(original_fits, folder_to_mirror,  param_path, vsys_init =None, pa_init=0, x_cen_init =0,  inp_max = 6.0, n_points = 120, vec_offsets = np.array([-1.4, -1.2, -1.0, -0.8, -0.6, -0.4, -0.2]), dsharp =True, only_fitting = False):

    basename = os.path.splitext(os.path.basename(original_fits))[0]


    # --- 1) Load data & estimate systemic velocity (vsys) ---
    if dsharp:
        data, x_arc, y_arc, vel_axis = mirrordisk_make.load_image_coordinate_velocity_from_fits(original_fits)
    else:
        data, x_arc, y_arc, vel_axis = mirrordisk_make.load_image_coordinate_velocity_from_dsharp_fits(original_fits)

    # If vsys_init is not provided, estimate it (e.g., using estimate_std or your preferred method)
    if vsys_init is None:
        vsys_init = mirrordisk_make.estimate_vsys_from_data(data, vel_axis)

    # --- 2) Prepare interpolator for optimization ---
    xx_inp, yy_inp = mirrordisk_make.make_coordinate_for_interpolation(inp_max, n_points)
    cube_interp = mirrordisk_make.make_interpolator_for_v_x_y_channel(vel_axis, x_arc, data)
    vec_val_arr = vec_offsets + vsys_init

    # Initial guess: [vsys, x_center=0, position_angle=0 (rad)]
    # — Extend this if you’d like to pass in an initial PA or other parameters
    initial_guess = [vsys_init, x_cen_init, pa_init]

    # --- 3) Run optimization ---
    t0 = time.time()
    result = mirrordisk_optimize.optimize_each_and_all(
        initial_guess, xx_inp, yy_inp, cube_interp, vec_val_arr
    )
    # Save optimized parameters
    np.save(param_path, result.x)
    if only_fitting:
        return 0

    # --- 4) Generate mirror FITS file ---
    mirror_fits = os.path.join(folder_to_mirror, basename + "_mirror.fits")
    mirrordisk_make.make_mirrors_fits(
        original_fits, mirror_fits, result.x, xx_inp, yy_inp, cube_interp
    )

    # --- 5) Generate residual FITS file ---
    data_mirror, *_ = mirrordisk_make.load_image_coordinate_velocity_from_fits(mirror_fits)
    hdul = fits.open(original_fits)
    hdul[0].data = data - data_mirror
    res_fits = os.path.join(folder_to_mirror, basename + "_res.fits")
    hdul.writeto(res_fits, overwrite=True)
    hdul.close()

    elapsed = time.time() - t0
    mem_mb = psutil.virtual_memory().used / (1024 ** 2)
    print(f"[{basename}] done in {elapsed:.1f}s, mem {mem_mb:.1f} MB")

    return {
        "params": param_path,
        "mirror_fits": mirror_fits,
        "residual_fits": res_fits,
    }

