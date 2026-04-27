from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.axes_grid1 import make_axes_locatable

from mirrordisk import mirrordisk_make


mpl.rcParams["font.size"] = 22
mpl.rcParams["axes.labelsize"] = 22


DV = 0.1
VLIM = 2.5
PLOT_LIM = 7.5
OUT_DIR = Path("./result/channel_maps/HD163296")

name = "HD163296"
image_fits = Path("/Volumes/T7 Shield/dsharp/data/HD163296_CO.fits")
mirror_fits = Path("/Volumes/T7 Shield/dsharp/mirror/HD163296_CO_mirror.fits")
res_fits = Path("/Volumes/T7 Shield/dsharp/mirror/HD163296_CO_res.fits")
params_npy = Path("/Volumes/T7 Shield/dsharp/mirror/HD163296_mirrorparams.npy")


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    original_cube, x_arcsec, _, velocity_axis = mirrordisk_make.load_image_coordinate_velocity_from_fits(
        image_fits
    )
    mirror_cube, _, _, _ = mirrordisk_make.load_image_coordinate_velocity_from_fits(mirror_fits)
    res_cube, _, _, _ = mirrordisk_make.load_image_coordinate_velocity_from_fits(res_fits)

    vsys, _, _ = np.load(params_npy)[:3]
    extent = (x_arcsec.max(), x_arcsec.min(), x_arcsec.min(), x_arcsec.max())
    channel_offsets = np.arange(-VLIM, VLIM + DV, DV)
    plot_vels = channel_offsets + vsys

    for j, plot_vel in enumerate(plot_vels):
        ci = int(np.argmin(np.abs(velocity_axis - plot_vel)))
        vel_offset = velocity_axis[ci] - vsys
        if np.abs(vel_offset) > VLIM:
            continue

        img_orig = original_cube[ci]
        img_mirror = mirror_cube[ci]
        img_res = res_cube[ci]

        fig, axes = plt.subplots(1, 3, figsize=(25, 8))
        data_list = [img_orig, img_mirror, img_res]
        titles = [
            rf"Original, $v={vel_offset:.2f}\,\mathrm{{km/s}}$",
            "Mirror",
            "Residual",
        ]

        vmax_orig = np.nanmax(img_orig)
        res_lim = np.nanmax(np.abs(img_orig))

        for ax, data, title in zip(axes, data_list, titles):
            if title == "Residual":
                im = ax.imshow(
                    data,
                    origin="lower",
                    cmap="bwr",
                    vmin=-res_lim,
                    vmax=res_lim,
                    extent=extent,
                )
            else:
                im = ax.imshow(
                    data,
                    origin="lower",
                    cmap="inferno",
                    vmin=0,
                    vmax=vmax_orig,
                    extent=extent,
                )

            ax.set_aspect("equal")
            ax.set_xlabel(r"$\Delta$RA [arcsec]")
            ax.set_ylabel(r"$\Delta$Dec [arcsec]")
            ax.set_title(title)
            ax.set_xlim(PLOT_LIM, -PLOT_LIM)
            ax.set_ylim(-PLOT_LIM, PLOT_LIM)

        divider = make_axes_locatable(axes[2])
        cax = divider.append_axes("right", size="5%", pad=0.05)
        fig.colorbar(im, cax=cax)

        plt.tight_layout()
        outfile = OUT_DIR / f"v_{j:03d}_{vel_offset:.2f}km_s.pdf"
        fig.savefig(outfile)
        plt.close(fig)


if __name__ == "__main__":
    main()
