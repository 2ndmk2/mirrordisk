import os
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from astrodendro import Dendrogram
from mirrordisk import mirrordisk_make
import plotly.io as pio
import plotly.graph_objects as go


def preprocess(name: str,
               lim: float,
               skip1: int,
               skip2: int,
               vlim: float,
               res_fits: Path,
               params_npy: Path,
               dsharp):
    """
    Load FITS data, apply velocity and spatial masks, and downsample.
    Returns reduced data cube, spatial coords, and velocity axis.
    """
    # Load residual FITS and systemic velocity
    # Read image cube and coordinates
    vsys = np.load(params_npy)[0]

    # Read image cube and coordinates
    if dsharp:
        data, x, y_arc, v= mirrordisk_make.load_image_coordinate_velocity_from_dsharp_fits(res_fits)
    else:
        data, x, y_arc, v = mirrordisk_make.load_image_coordinate_velocity_from_fits(res_fits)
    vel = v - vsys

    # Velocity mask
    mask_v = np.abs(vel) < vlim
    # Spatial mask (x and y within lim)
    mask_xy = np.abs(x) < lim

    # Apply masks and downsample
    data_r = data[mask_v][:, mask_xy, :][:, :, mask_xy]
    data_r = data_r[::skip2, ::skip1, ::skip1]
    vel_r = vel[mask_v][::skip2]
    x_r = x[mask_xy][::skip1]

    return data_r, x_r, vel_r


def compute_dendro_mask(data: np.ndarray,n_sigma: float,  min_npix: int) -> np.ndarray:
    """
    Compute dendrogram on the data cube; return a boolean mask of significant structures.
    """
    # Estimate noise from first channel
    vmin, vmax = np.percentile(data[0], [20, 80])
    sigma = np.std(data[(data > vmin) & (data < vmax)])

    # Build dendrogram and aggregate leaf masks
    d = Dendrogram.compute(data, min_value=n_sigma * sigma, min_npix=min_npix)
    mask = np.zeros_like(data, dtype=bool)
    for leaf in d.leaves:
        mask |= leaf.get_mask()
    return mask


def compute_moments(masked: np.ndarray, vel_r: np.ndarray):
    """
    Compute zeroth (integrated intensity) and first (intensity-weighted
    velocity) moments from masked data cube.
    """
    dv = vel_r[1] - vel_r[0]
    m0 = np.nansum(masked, axis=0) * dv
    m1 = (np.nansum(masked * vel_r[:, None, None], axis=0) * dv) / (m0 + 1e-30)
    return m0, m1


def compute_moment_n(masked: np.ndarray, vel_r: np.ndarray, n: int, normalize: bool = True):
    """
    Compute the n-th velocity moment from a masked data cube.

    If normalize is True, returns the intensity-weighted moment
    sum(I * v^n) / sum(I). Otherwise returns the raw moment sum(I * v^n) dv.
    """
    dv = vel_r[1] - vel_r[0]
    numerator = np.nansum(masked * vel_r[:, None, None] ** n, axis=0) * dv
    if not normalize:
        return numerator

    m0 = np.nansum(masked, axis=0) * dv
    return numerator / (m0 + 1e-30)


def plot_moments(m0: np.ndarray, m1: np.ndarray, x_r: np.ndarray, name: str, out_dir: Path, pos:bool):
    """
    Plot and save moment0 and moment1 side by side as PDF.
    """
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    extent = [x_r.max(), x_r.min(), x_r.min(), x_r.max()]

    if pos:

        # Moment-0 map
        im0 = axes[0].imshow(m0, origin='lower', extent=extent)
        axes[0].set(
            title=f"{name} Moment0",
            xlabel='ΔRA [arcsec]',
            ylabel='ΔDec [arcsec]'
        )
        fig.colorbar(im0, ax=axes[0], label='Jy/beam km/s')

        # Moment-1 map
        im1 = axes[1].imshow(m1, origin='lower', cmap='bwr', extent=extent)
        axes[1].set(
            title=f"{name} Moment1",
            xlabel='ΔRA [arcsec]',
            ylabel='ΔDec [arcsec]'
        )
        fig.colorbar(im1, ax=axes[1], label='km/s')

        fig.tight_layout()
        fig.savefig(os.path.join(out_dir, f"{name}_mom.pdf"),  dpi=300)
    else:        
        
        # Moment-0 map
        im0 = axes[0].imshow(-m0, origin='lower', extent=extent)
        axes[0].set(
            title=f"{name} Moment0",
            xlabel='ΔRA [arcsec]',
            ylabel='ΔDec [arcsec]'
        )
        fig.colorbar(im0, ax=axes[0], label='Jy/beam km/s')

        # Moment-1 map
        im1 = axes[1].imshow(m1, origin='lower', cmap='bwr', extent=extent)
        axes[1].set(
            title=f"{name} Moment1",
            xlabel='ΔRA [arcsec]',
            ylabel='ΔDec [arcsec]'
        )
        fig.colorbar(im1, ax=axes[1], label='km/s')

        fig.tight_layout()    
        fig.savefig(os.path.join(out_dir, f"{name}_mom_neg.pdf"),  dpi=300)
    plt.close(fig)

def plot_moments_vlim(m0: np.ndarray, m1: np.ndarray, x_r: np.ndarray, name: str, out_dir: Path, pos:bool, vlim = 2.5):
    """
    Plot and save moment0 and moment1 side by side as PDF.
    """
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    extent = [x_r.max(), x_r.min(), x_r.min(), x_r.max()]


    # Moment-0 map
    im0 = axes[0].imshow(m0, origin='lower', extent=extent)
    axes[0].set(
        title=f"{name} Moment0",
        xlabel='ΔRA [arcsec]',
        ylabel='ΔDec [arcsec]'
    )
    fig.colorbar(im0, ax=axes[0], label='Jy/beam km/s')

    # Moment-1 map
    im1 = axes[1].imshow(m1, origin='lower', cmap='bwr', extent=extent, vmin = -vlim, vmax = vlim)
    axes[1].set(
        title=f"{name} Moment1",
        xlabel='ΔRA [arcsec]',
        ylabel='ΔDec [arcsec]'
    )

    fig.colorbar(im1, ax=axes[1], label='km/s')

    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, f"{name}_mom.pdf"),  dpi=300)

    plt.close(fig)


def plot_scalar_map(map_data: np.ndarray,
                    x_r: np.ndarray,
                    name: str,
                    out_dir: Path,
                    label: str,
                    cmap: str = 'viridis',
                    symmetric: bool = False):
    """
    Plot and save a single 2D map such as a higher-order moment.
    """
    fig, ax = plt.subplots(1, 1, figsize=(6, 5))
    extent = [x_r.max(), x_r.min(), x_r.min(), x_r.max()]

    kwargs = {}
    if symmetric:
        vmax = np.nanmax(np.abs(map_data))
        kwargs.update(vmin=-vmax, vmax=vmax)

    im = ax.imshow(map_data, origin='lower', extent=extent, cmap=cmap, **kwargs)
    ax.set(
        title=f"{name} {label}",
        xlabel='ΔRA [arcsec]',
        ylabel='ΔDec [arcsec]'
    )
    fig.colorbar(im, ax=ax, label=label)
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, f"{name}_{label.replace(' ', '_').lower()}.pdf"), dpi=300)
    plt.close(fig)



def save_isosurface_html(X: np.ndarray,
                         Y: np.ndarray,
                         Z: np.ndarray,
                         data_convert: np.ndarray,
                         contour_value: float,
                         lim: float,
                         name: str,
                         out_dir: str):
    """
    Generate and save an isosurface 3D plot as an interactive HTML file.
    Red surface for +contour_value and blue for -contour_value.
    """
    # prepare figure
    fig = go.Figure(
        data=go.Isosurface(
            x=-X.flatten(), y=Y.flatten(), z=Z.flatten(), value=data_convert.flatten(),
            isomin=contour_value, isomax=contour_value,
            opacity=0.1, surface_count=1, colorscale=[[0, 'red'], [1, 'red']]
        )
    )
    fig.add_trace(
        go.Isosurface(
            x=-X.flatten(), y=Y.flatten(), z=Z.flatten(), value=data_convert.flatten(),
            isomin=-contour_value, isomax=-contour_value,
            opacity=0.1, surface_count=1, colorscale=[[0, 'blue'], [1, 'blue']]
        )
    )
    # update axes labels and limits
    fig.update_layout(
        scene=dict(
            xaxis_title='Delta RA (arcsec)',
            yaxis=dict(title='Delta Dec (arcsec)', range=[lim, -lim]),
            zaxis_title='Velocity [km/s]'
        )
    )
    # ensure output directory
    out_dir.mkdir(parents=True, exist_ok=True)
    # write HTML
    outfile = out_dir / f"isosurface_zoom_{name}.html"
    pio.write_html(fig, str(outfile))
