from astropy.io import fits
import numpy as np
import astropy.constants as const
from scipy.interpolate import RegularGridInterpolator
from scipy.optimize import minimize

def to_3d(array: np.ndarray) -> np.ndarray:

    if array.ndim == 4 and array.shape[0] == 1:
        # 先頭の次元 (サイズ1) を除去
        return array[0]
    else:
        return array
    
def load_image_coordinate_from_fits(fitsfile):
    """
    Load image data, coordinate axes, and velocity axis from a FITS file.

    Parameters
    ----------
    fitsfile : str
        Path to the FITS file.

    Returns
    -------
    data : numpy.ndarray
        Image data array.
    x_coord_arcsec : numpy.ndarray
        Array of x-coordinates in arcseconds.
    y_coord_arcsec : numpy.ndarray
        Array of y-coordinates in arcseconds.
    velocity_axis : numpy.ndarray
        Array of velocity values in km/s.
    """
    hdulist = fits.open(fitsfile)
    data = hdulist[0].data
    data = to_3d(data)
    header = hdulist[0].header
    x_num = header["NAXIS1"]
    cdelt2 = header['CDELT2']
    x_coord_arcsec = np.arange(x_num ) * cdelt2 * 3600
    x_coord_arcsec -= np.mean(x_coord_arcsec)
    y_coord_arcsec = np.arange(x_num ) * cdelt2 * 3600
    y_coord_arcsec -= np.mean(y_coord_arcsec)
    hdulist.close() 
    return data, x_coord_arcsec, y_coord_arcsec

def load_image_coordinate_velocity_from_fits(fitsfile):
    """
    Load image data, coordinate axes, and velocity axis from a FITS file.

    Parameters
    ----------
    fitsfile : str
        Path to the FITS file.

    Returns
    -------
    data : numpy.ndarray
        Image data array.
    x_coord_arcsec : numpy.ndarray
        Array of x-coordinates in arcseconds.
    y_coord_arcsec : numpy.ndarray
        Array of y-coordinates in arcseconds.
    velocity_axis : numpy.ndarray
        Array of velocity values in km/s.
    """
    hdulist = fits.open(fitsfile)
    data = hdulist[0].data
    data = to_3d(data)
    shape = data.shape
    header = hdulist[0].header
    velocity_axis = np.arange(1, header["NAXIS3"]+1)
    x_num = header["NAXIS1"]
    spec_nu_rest = header["RESTFRQ"]
    cdelt2 = header['CDELT2']
    crval3 = header['CRVAL3']
    cdelt3 = header['CDELT3']
    crpix3 = header['CRPIX3']
    freq = crval3 + (velocity_axis - crpix3) * cdelt3
    c = const.c.value
    velocity_axis = c * (spec_nu_rest - freq) / spec_nu_rest / 1000
    x_coord_arcsec = np.arange(x_num ) * cdelt2 * 3600
    x_coord_arcsec -= np.mean(x_coord_arcsec)
    y_coord_arcsec = np.arange(x_num ) * cdelt2 * 3600
    y_coord_arcsec -= np.mean(y_coord_arcsec)
    hdulist.close() 
    return data, x_coord_arcsec, y_coord_arcsec, velocity_axis

def load_image_coordinate_velocity_from_dsharp_fits(fitsfile):
    """
    Load image data, coordinate axes, and velocity axis from a FITS file.

    Parameters
    ----------
    fitsfile : str
        Path to the FITS file.

    Returns
    -------
    data : numpy.ndarray
        Image data array.
    x_coord_arcsec : numpy.ndarray
        Array of x-coordinates in arcseconds.
    y_coord_arcsec : numpy.ndarray
        Array of y-coordinates in arcseconds.
    velocity_axis : numpy.ndarray
        Array of velocity values in km/s.
    """
    hdulist = fits.open(fitsfile)
    data = hdulist[0].data
    data = to_3d(data)
    shape = data.shape
    header = hdulist[0].header
    spec_nu_rest = header["RESTFRQ"]
    cdelt2 = header['CDELT1']
    crval3 = header['CRVAL3']
    cdelt3 = header['CDELT3']
    crpix3 = header['CRPIX3']
    npix3 = header['NAXIS3']
    velocity_axis = np.arange(1, npix3+1 )
    freq = crval3 + (velocity_axis - crpix3) * cdelt3
    c = const.c.value
    velocity_axis = c * (spec_nu_rest - freq) / spec_nu_rest / 1000
    x_coord_arcsec = np.arange(shape[1]) * cdelt2 * 3600
    x_coord_arcsec -= np.mean(x_coord_arcsec)
    y_coord_arcsec = np.arange(shape[1]) * cdelt2 * 3600
    y_coord_arcsec -= np.mean(y_coord_arcsec)
    hdulist.close() 
    return data,- x_coord_arcsec, -y_coord_arcsec, velocity_axis

def load_frequency_from_dsharp_fits(fitsfile):
    """
    Load frequency from a FITS file.

    Parameters
    ----------
    fitsfile : str
        Path to the FITS file.

    Returns
    -------
    freq : numpy.ndarray
    """
    hdulist = fits.open(fitsfile)
    header = hdulist[0].header
    crval3 = header['CRVAL3']
    cdelt3 = header['CDELT3']
    crpix3 = header['CRPIX3']
    npix3 = header['NAXIS3']
    velocity_axis = np.arange(1, npix3+1 )
    freq = crval3 + (velocity_axis - crpix3) * cdelt3
    return freq


def make_coordinate_for_interpolation(lim_max, n_points):
    """
    Create a coordinate grid for interpolation.

    Parameters
    ----------
    lim_max : float
        The maximum limit for the grid in both x and y directions.
    n_points : int
        Number of points in each direction.

    Returns
    -------
    xx_inp : numpy.ndarray
        2D array of x-coordinates.
    yy_inp : numpy.ndarray
        2D array of y-coordinates.
    """
    x_inp = np.linspace(-lim_max, lim_max, n_points)
    y_inp = np.linspace(-lim_max, lim_max, n_points)
    xx_inp, yy_inp = np.meshgrid(x_inp, y_inp)
    return xx_inp, yy_inp

def make_interpolator_for_v_x_y_channel(velocity_axis, x_coord_arcsec, data):
    """
    Create an interpolator for the given data.

    Parameters
    ----------
    velocity_axis : numpy.ndarray
        Array of velocity values.
    x_coord_arcsec : numpy.ndarray
        Array of x-coordinates in arcseconds.
    data : numpy.ndarray
        Image data array.

    Returns
    -------
    interpolator : scipy.interpolate.RegularGridInterpolator
        Interpolator for the data.
    """
    interpolator = RegularGridInterpolator((velocity_axis, x_coord_arcsec, x_coord_arcsec), data, bounds_error=False, fill_value=None)
    return interpolator




def make_residual_fits(original_fits, out_fits, params, xx_inp, yy_inp, interpolator):
    """
    Create a FITS file with residuals.

    Parameters
    ----------
    original_fits : str
        Path to the original FITS file.
    out_fits : str
        Path to the output FITS file.
    params : list of float
        List of parameters [vsys, x_cen, pa_rad].
    xx_inp : numpy.ndarray
        2D array of x-coordinates.
    yy_inp : numpy.ndarray
        2D array of y-coordinates.
    interpolator : scipy.interpolate.RegularGridInterpolator
        Interpolator for the data.

    Returns
    -------
    data : numpy.ndarray
        Residual data array.
    """
    hdulist = fits.open(original_fits)
    data, x_coord_arcsec, y_coord_arcsec, velocity_axis = load_image_coordinate_velocity_from_fits(original_fits)
    xx, yy = np.meshgrid(x_coord_arcsec, x_coord_arcsec)
    for (i, vec_val) in enumerate(velocity_axis):
        if i % 50==0:
            print("%d/%d" % (i, len(velocity_axis)))
        image_vec_val, image_vec_sym = make_line_sym_image(interpolator, xx, yy, vec_val, params[0], params[1], params[2])
        res = image_vec_val - image_vec_sym
        data[i] = res
    hdulist[0].data = data
    hdulist.writeto(out_fits, overwrite=True)
    return data

def make_mirrors_fits(original_fits, out_fits, params, xx_inp, yy_inp, interpolator):
    """
    Create a FITS file with residuals.

    Parameters
    ----------
    original_fits : str
        Path to the original FITS file.
    out_fits : str
        Path to the output FITS file.
    params : list of float
        List of parameters [vsys, x_cen, pa_rad].
    xx_inp : numpy.ndarray
        2D array of x-coordinates.
    yy_inp : numpy.ndarray
        2D array of y-coordinates.
    interpolator : scipy.interpolate.RegularGridInterpolator
        Interpolator for the data.

    Returns
    -------
    data : numpy.ndarray
        Residual data array.
    """
    hdulist = fits.open(original_fits)
    data, x_coord_arcsec, y_coord_arcsec, velocity_axis = load_image_coordinate_velocity_from_fits(original_fits)
    xx, yy = np.meshgrid(x_coord_arcsec, x_coord_arcsec)
    for (i, vec_val) in enumerate(velocity_axis):
        if i % 50==0:
            print("%d/%d" % (i, len(velocity_axis)))
        image_vec_val, image_vec_sym = make_line_sym_image(interpolator, xx, yy, vec_val, params[0], params[1], params[2])
        data[i] = image_vec_sym
    hdulist[0].data = data
    hdulist.writeto(out_fits, overwrite=True)
    return data

def make_mirror_from_res_fits(original_fits, res_fits, out_fits):
    """
    Create a FITS file with residuals.

    Parameters
    ----------
    original_fits : str
        Path to the original FITS file.
    out_fits : str
        Path to the output FITS file.
    params : list of float
        List of parameters [vsys, x_cen, pa_rad].
    xx_inp : numpy.ndarray
        2D array of x-coordinates.
    yy_inp : numpy.ndarray
        2D array of y-coordinates.
    interpolator : scipy.interpolate.RegularGridInterpolator
        Interpolator for the data.

    Returns
    -------
    data : numpy.ndarray
        Residual data array.
    """
    hdulist = fits.open(original_fits)
    data, x_coord_arcsec, y_coord_arcsec, velocity_axis = load_image_coordinate_velocity_from_fits(original_fits)
    data_res, x_coord_arcsec, y_coord_arcsec, velocity_axis = load_image_coordinate_velocity_from_fits(res_fits)
    data_mirror =  np.copy(data - data_res)
    del data
    del data_res
    hdulist[0].data = data_mirror
    hdulist.writeto(out_fits, overwrite=True)
    return data

def return_line_symmetry(xx, yy,  x_cen, pa_rad):
    """
    Calculate the symmetric coordinates across a line defined by position angle and center.

    Parameters
    ----------
    xx : numpy.ndarray
        Array of x-coordinates.
    yy : numpy.ndarray
        Array of y-coordinates.
    pa_rad : float
        Position angle in radians.
    x_cen : float
        Center x-coordinate.

    Returns
    -------
    xx_prime : numpy.ndarray
        Symmetric x-coordinates.
    yy_prime : numpy.ndarray
        Symmetric y-coordinates.
    """
    a =  np.tan(pa_rad)
    b = -a * x_cen
    x0 = (a * yy + xx - a * b) / (a ** 2 + 1)
    y0 = (yy * (a ** 2) + a * xx + b) / (a ** 2 + 1)
    xx_prime = 2 * x0 - xx
    yy_prime = 2 * y0 - yy
    return xx_prime, yy_prime

def make_line_sym_image(interpolator, xx_inp, yy_inp, vec_val, vsys, x_cen, pa_rad):
    """
    Generate symmetric images for a given velocity value.

    Parameters
    ----------
    interpolator : scipy.interpolate.RegularGridInterpolator
        Interpolator for the data.
    xx_inp : numpy.ndarray
        2D array of x-coordinates.
    yy_inp : numpy.ndarray
        2D array of y-coordinates.
    vec_val : float
        Velocity value.
    vsys : float
        Systemic velocity.
    pa_rad : float
        Position angle in radians.
    x_cen : float
        Center x-coordinate.

    Returns
    -------
    image_vec_val : numpy.ndarray
        Interpolated image for the given velocity value.
    image_vec_sym : numpy.ndarray
        Symmetric interpolated image for the given velocity value.
    """
    xx_prime_prime, yy_prime_prime = return_line_symmetry(xx_inp, yy_inp, x_cen,  pa_rad)
    vec_now = np.ones_like(xx_prime_prime) * vec_val
    new_points = np.array([vec_now.flatten(), yy_inp.flatten(), xx_inp.flatten()]).T
    vdif = 2 * vsys - vec_now
    new_points2 = np.array([vdif.flatten(), yy_prime_prime.flatten(), xx_prime_prime.flatten()]).T
    image_vec_val = interpolator(new_points)
    image_vec_sym = interpolator(new_points2)
    image_vec_val = image_vec_val.reshape(xx_inp.shape)
    image_vec_sym = image_vec_sym.reshape(xx_inp.shape)

    del new_points
    del new_points2
    return image_vec_val, image_vec_sym



#####


def return_line_symmetry_prev(xx, yy,  x_cen, pa_rad):
    """
    Calculate the symmetric coordinates across a line defined by position angle and center.

    Parameters
    ----------
    xx : numpy.ndarray
        Array of x-coordinates.
    yy : numpy.ndarray
        Array of y-coordinates.
    pa_rad : float
        Position angle in radians.
    x_cen : float
        Center x-coordinate.

    Returns
    -------
    xx_prime : numpy.ndarray
        Symmetric x-coordinates.
    yy_prime : numpy.ndarray
        Symmetric y-coordinates.
    """
    a = 1 / np.tan(pa_rad)
    b = -a * x_cen
    x0 = (a * yy + xx - a * b) / (a ** 2 + 1)
    y0 = (yy * (a ** 2) + a * xx + b) / (a ** 2 + 1)
    xx_prime = 2 * x0 - xx
    yy_prime = 2 * y0 - yy
    return xx_prime, yy_prime

def make_line_sym_image_prev(interpolator, xx_inp, yy_inp, vec_val, vsys, x_cen, pa_rad):
    """
    Generate symmetric images for a given velocity value.

    Parameters
    ----------
    interpolator : scipy.interpolate.RegularGridInterpolator
        Interpolator for the data.
    xx_inp : numpy.ndarray
        2D array of x-coordinates.
    yy_inp : numpy.ndarray
        2D array of y-coordinates.
    vec_val : float
        Velocity value.
    vsys : float
        Systemic velocity.
    pa_rad : float
        Position angle in radians.
    x_cen : float
        Center x-coordinate.

    Returns
    -------
    image_vec_val : numpy.ndarray
        Interpolated image for the given velocity value.
    image_vec_sym : numpy.ndarray
        Symmetric interpolated image for the given velocity value.
    """
    xx_prime_prime, yy_prime_prime = return_line_symmetry(xx_inp, yy_inp, x_cen,  pa_rad)
    vec_now = np.ones_like(xx_prime_prime) * vec_val
    new_points = np.array([vec_now, xx_inp, yy_inp]).T
    new_points2 = np.array([2 * vsys - vec_now, xx_prime_prime, yy_prime_prime]).T
    image_vec_val = interpolator(new_points)
    image_vec_sym = interpolator(new_points2)

    del new_points
    del new_points2
    return image_vec_val, image_vec_sym


def estimate_vsys_from_data(data, velocity_axis, ratio = 0.45):
    print(np.shape(data))

    nz, nx, ny = np.shape(data)
    dx = int(nx * ratio)
    data_red = data[:,dx :nx-dx ,dx:ny-dx]
    flux_sum = np.sum(data_red, axis=(1,2))
    vsys = np.sum(velocity_axis * flux_sum)/np.sum(flux_sum)
    return vsys