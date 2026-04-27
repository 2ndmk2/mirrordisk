from astropy.io import fits
import jax.numpy as np
import astropy.constants as const
from jax.scipy.optimize import minimize
from asymmvelo import asymm_make_jax as asymm_make


def compute_res_asym_vsys_pa_fixed(params, vsys, pa_rad, xx_inp, yy_inp, interpolator, vec_val_arr):
    """
    Compute the residual asymmetry with fixed vsys and position angle.

    Parameters
    ----------
    params : list of float
        List of parameters [vsys, x_cen].
    pa_rad : float
        Position angle in radians.
    xx_inp : numpy.ndarray
        2D array of x-coordinates.
    yy_inp : numpy.ndarray
        2D array of y-coordinates.
    interpolator : scipy.interpolate.RegularGridInterpolator
        Interpolator for the data.
    vec_val_arr : numpy.ndarray
        Array of velocity values.

    Returns
    -------
    res_now : float
        Residual asymmetry value.
    """
    res_now = 0
    x_cen = params[0]
    for vec_val in vec_val_arr:
        image_vec_val, image_vec_sym =asymm_make.make_line_sym_image(interpolator, xx_inp, yy_inp, vec_val, vsys, x_cen,  pa_rad)
        res_now +=np.sum( (image_vec_val - image_vec_sym) ** 2)/(np.std(image_vec_val)**2)
    return np.sqrt(res_now)

def compute_res_asym_x_cen_pa_fixed(params, x_cen, pa_rad, xx_inp, yy_inp, interpolator, vec_val_arr):
    """
    Compute the residual asymmetry with fixed xcen and position angle.

    Parameters
    ----------
    params : list of float
        List of parameters [vsys, x_cen].
    pa_rad : float
        Position angle in radians.
    xx_inp : numpy.ndarray
        2D array of x-coordinates.
    yy_inp : numpy.ndarray
        2D array of y-coordinates.
    interpolator : scipy.interpolate.RegularGridInterpolator
        Interpolator for the data.
    vec_val_arr : numpy.ndarray
        Array of velocity values.

    Returns
    -------
    res_now : float
        Residual asymmetry value.
    """
    res_now = 0
    vsys = params[0]
    for vec_val in vec_val_arr:
        image_vec_val, image_vec_sym =asymm_make.make_line_sym_image(interpolator, xx_inp, yy_inp, vec_val, vsys, x_cen,  pa_rad)
        res_now +=np.sum( (image_vec_val - image_vec_sym) ** 2)/(np.std(image_vec_val)**2)
    return np.sqrt(res_now)

def compute_res_asym_pa_fixed(params, pa_rad, xx_inp, yy_inp, interpolator, vec_val_arr):
    """
    Compute the residual asymmetry with fixed position angle.

    Parameters
    ----------
    params : list of float
        List of parameters [vsys, x_cen].
    pa_rad : float
        Position angle in radians.
    xx_inp : numpy.ndarray
        2D array of x-coordinates.
    yy_inp : numpy.ndarray
        2D array of y-coordinates.
    interpolator : scipy.interpolate.RegularGridInterpolator
        Interpolator for the data.
    vec_val_arr : numpy.ndarray
        Array of velocity values.

    Returns
    -------
    res_now : float
        Residual asymmetry value.
    """
    res_now = 0
    vsys = params[0]
    x_cen = params[1]
    for vec_val in vec_val_arr:
        image_vec_val, image_vec_sym =asymm_make.make_line_sym_image(interpolator, xx_inp, yy_inp, vec_val, vsys, x_cen,  pa_rad)
        res_now +=np.sum( (image_vec_val - image_vec_sym) ** 2)/(np.std(image_vec_val)**2)
    return res_now

def compute_res_asym(params, xx_inp, yy_inp, interpolator, vec_val_arr):
    """
    Compute the residual asymmetry for the given parameters.

    Parameters
    ----------
    params : list of float
        List of parameters [vsys, x_cen, pa_rad].
    xx_inp : numpy.ndarray
        2D array of x-coordinates.
    yy_inp : numpy.ndarray
        2D array of y-coordinates.
    interpolator : scipy.interpolate.RegularGridInterpolator
        Interpolator for the data.
    vec_val_arr : numpy.ndarray
        Array of velocity values.

    Returns
    -------
    res_now : float
        Residual asymmetry value.
    """
    res_now = 0
    vsys = params[0]
    x_cen = params[1]
    pa_rad = params[2]
    for vec_val in vec_val_arr:
        image_vec_val, image_vec_sym = asymm_make.make_line_sym_image(interpolator, xx_inp, yy_inp, vec_val, vsys, x_cen, pa_rad)
        res_now +=np.sum( (image_vec_val - image_vec_sym) ** 2)/(np.std(image_vec_val)**2)
    return res_now

def optimize_xcen(initial_guess, xx_inp, yy_inp, interpolator, vec_val_arr):
    """
    Optimize the xcen with fixed other parameters.

    Parameters
    ----------
    initial_guess : list of float
        Initial guess for [vsys, x_cen, pa_rad].
    xx_inp : numpy.ndarray
        2D array of x-coordinates.
    yy_inp : numpy.ndarray
        2D array of y-coordinates.
    interpolator : scipy.interpolate.RegularGridInterpolator
        Interpolator for the data.
    vec_val_arr : numpy.ndarray
        Array of velocity values.

    Returns
    -------
    result : scipy.optimize.OptimizeResult
        Result of the optimization.
    """
    vsys = initial_guess[0]
    pa_rad = initial_guess[2]
    result = minimize(compute_res_asym_vsys_pa_fixed, initial_guess[1], args=(vsys, pa_rad, xx_inp, yy_inp, interpolator, vec_val_arr), method="BFGS")
    return result

def optimize_vsys(initial_guess, xx_inp, yy_inp, interpolator, vec_val_arr):
    """
    Optimize the systemic velocity with fixed other parameters.

    Parameters
    ----------
    initial_guess : list of float
        Initial guess for [vsys, x_cen, pa_rad].
    xx_inp : numpy.ndarray
        2D array of x-coordinates.
    yy_inp : numpy.ndarray
        2D array of y-coordinates.
    interpolator : scipy.interpolate.RegularGridInterpolator
        Interpolator for the data.
    vec_val_arr : numpy.ndarray
        Array of velocity values.

    Returns
    -------
    result : scipy.optimize.OptimizeResult
        Result of the optimization.
    """
    x_cen = initial_guess[1]
    pa_rad = initial_guess[2]
    result = minimize(compute_res_asym_x_cen_pa_fixed, initial_guess[:1], args=(x_cen, pa_rad, xx_inp, yy_inp, interpolator, vec_val_arr), method="BFGS")
    return result

def optimize_vsys_xcen(initial_guess, xx_inp, yy_inp, interpolator, vec_val_arr):
    """
    Optimize the systemic velocity and center x-coordinate with fixed position angle.

    Parameters
    ----------
    initial_guess : list of float
        Initial guess for [vsys, x_cen, pa_rad].
    xx_inp : numpy.ndarray
        2D array of x-coordinates.
    yy_inp : numpy.ndarray
        2D array of y-coordinates.
    interpolator : scipy.interpolate.RegularGridInterpolator
        Interpolator for the data.
    vec_val_arr : numpy.ndarray
        Array of velocity values.

    Returns
    -------
    result : scipy.optimize.OptimizeResult
        Result of the optimization.
    """
    pa_rad = initial_guess[2]
    result = minimize(compute_res_asym_pa_fixed, initial_guess[:2], args=(pa_rad, xx_inp, yy_inp, interpolator, vec_val_arr), method="BFGS")
    return result

def optimize_vsys_xcen_pa(initial_guess, xx_inp, yy_inp, interpolator, vec_val_arr):
    """
    Optimize the systemic velocity, center x-coordinate, and position angle.

    Parameters
    ----------
    initial_guess : list of float
        Initial guess for [vsys, x_cen, pa_rad].
    xx_inp : numpy.ndarray
        2D array of x-coordinates.
    yy_inp : numpy.ndarray
        2D array of y-coordinates.
    interpolator : scipy.interpolate.RegularGridInterpolator
        Interpolator for the data.
    vec_val_arr : numpy.ndarray
        Array of velocity values.

    Returns
    -------
    result : scipy.optimize.OptimizeResult
        Result of the optimization.
    """
    result = minimize(compute_res_asym, initial_guess, args=(xx_inp, yy_inp, interpolator, vec_val_arr), method="BFGS")
    return result

def optimize_each_and_all(initial_guess, xx_inp, yy_inp, interpolator, vec_val_arr):
    """
    Parameters optimzation for systemic velocity, center x-coordinate, and position angle in consecutive manners. 
    (1) Optimize only systematic velocity with other parmaeters being fixed
    (2) Optimize only x_cen with other parmaeters being fixed (vsys is obtained by (1))
    (3) Joint optimization of all parameters ((vsys, x_cen) are obtained by (1) and (2)) 

    Parameters
    ----------
    initial_guess : list of float
        Initial guess for [vsys, x_cen, pa_rad].
    xx_inp : numpy.ndarray
        2D array of x-coordinates.
    yy_inp : numpy.ndarray
        2D array of y-coordinates.
    interpolator : scipy.interpolate.RegularGridInterpolator
        Interpolator for the data.
    vec_val_arr : numpy.ndarray
        Array of velocity values.

    Returns
    -------
    result : scipy.optimize.OptimizeResult
        Result of the optimization.
    """

    result_xcen_pa_fixed = optimize_vsys( initial_guess, xx_inp, yy_inp,  interpolator, vec_val_arr)
    initial_guess_update = np.copy( initial_guess)
    initial_guess_update [0] = result_xcen_pa_fixed.x[0]
    result_vsys_pa_fixed = optimize_xcen( initial_guess_update, xx_inp, yy_inp,  interpolator, vec_val_arr)
    initial_guess_update [1] = result_vsys_pa_fixed.x[0]
    result_all_fit_update = optimize_vsys_xcen_pa( initial_guess_update, xx_inp, yy_inp,  interpolator, vec_val_arr)

    return result_all_fit_update

