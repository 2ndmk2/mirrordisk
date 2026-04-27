from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.axes_grid1 import make_axes_locatable

from . import mirror, mirrordisk_make, mirrordisk_res_ana


@dataclass(frozen=True)
class MirrorProcessingConfig:
    source_name: str = ""
    source_fits_name: str = ""
    pa_deg_initial: float = 0.0
    x_cen_initial: float = 0.0
    vsys_initial: float | None = None
    inp_max: float = 6.0
    n_points: int = 120
    vec_offsets: np.ndarray = field(
        default_factory=lambda: np.array([-1.4, -1.2, -1.0, -0.8, -0.6, -0.4, -0.2])
    )


@dataclass(frozen=True)
class ChannelMapConfig:
    dv: float = 0.1
    vlim: float = 2.5
    plot_lim: float = 7.5
    font_size: int = 22
    axes_labelsize: int = 22


@dataclass(frozen=True)
class HtmlConfig:
    skip1: int = 3
    skip2: int = 1
    vlim: float = 2.5
    plot_lim: float = 5.0
    contour_sigma: float = 6.5


@dataclass(frozen=True)
class ResidualAnalysisConfig:
    skip1: int = 1
    skip2: int = 1
    vlim: float = 2.5
    min_npix: int = 1000
    nsigma: int = 5
    plot_lim: float = 5.0


@dataclass(frozen=True)
class MirrorPaths:
    source_fits: Path
    mirror_dir: Path
    param_prefix: Path
    params_npy: Path
    mirror_fits: Path
    residual_fits: Path


def build_mirror_paths(source_fits: str | Path, mirror_dir: str | Path) -> MirrorPaths:
    source_path = Path(source_fits)
    output_dir = Path(mirror_dir)
    stem = source_path.stem
    return MirrorPaths(
        source_fits=source_path,
        mirror_dir=output_dir,
        param_prefix=output_dir / f"{stem}_mirrorparams",
        params_npy=output_dir / f"{stem}_mirrorparams.npy",
        mirror_fits=output_dir / f"{stem}_mirror.fits",
        residual_fits=output_dir / f"{stem}_res.fits",
    )


def resolve_generated_file(expected: str | Path, mirror_dir: str | Path, suffix: str) -> Path:
    expected_path = Path(expected)
    if expected_path.exists():
        return expected_path

    mirror_path = Path(mirror_dir)
    stem = expected_path.stem
    stem_without_image = stem.removesuffix(".image")
    for candidate_stem in (stem, stem_without_image):
        candidate = mirror_path / f"{candidate_stem}{suffix}"
        if candidate.exists():
            return candidate

    matches = sorted(mirror_path.glob(f"*{suffix}"))
    if len(matches) == 1:
        return matches[0]

    return expected_path


def generate_mirror_products(
    source_fits: str | Path,
    mirror_dir: str | Path,
    config: MirrorProcessingConfig,
):
    paths = build_mirror_paths(source_fits, mirror_dir)
    pa_rad_initial = np.deg2rad(config.pa_deg_initial)
    paths.mirror_dir.mkdir(parents=True, exist_ok=True)
    return mirror.process_fits_file(
        str(paths.source_fits),
        f"{str(paths.mirror_dir)}/",
        str(paths.param_prefix),
        vsys_init=config.vsys_initial,
        pa_init=pa_rad_initial,
        x_cen_init=config.x_cen_initial,
        inp_max=config.inp_max,
        n_points=config.n_points,
        vec_offsets=config.vec_offsets,
    )


def generate_channel_maps(
    source_name: str,
    source_fits: str | Path,
    mirror_dir: str | Path,
    out_dir: str | Path,
    config: ChannelMapConfig,
):
    paths = build_mirror_paths(source_fits, mirror_dir)
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    mpl.rcParams["font.size"] = config.font_size
    mpl.rcParams["axes.labelsize"] = config.axes_labelsize

    mirror_fits = resolve_generated_file(paths.mirror_fits, paths.mirror_dir, "_mirror.fits")
    residual_fits = resolve_generated_file(paths.residual_fits, paths.mirror_dir, "_res.fits")
    params_npy = resolve_generated_file(paths.params_npy, paths.mirror_dir, "_mirrorparams.npy")

    original_cube, x_arcsec, _, velocity_axis = mirrordisk_make.load_image_coordinate_velocity_from_fits(
        paths.source_fits
    )
    mirror_cube, _, _, _ = mirrordisk_make.load_image_coordinate_velocity_from_fits(mirror_fits)
    residual_cube, _, _, _ = mirrordisk_make.load_image_coordinate_velocity_from_fits(residual_fits)

    vsys = np.load(params_npy)[0]
    extent = (x_arcsec.max(), x_arcsec.min(), x_arcsec.min(), x_arcsec.max())
    channel_offsets = np.arange(-config.vlim, config.vlim + config.dv, config.dv)
    plot_velocities = channel_offsets + vsys

    for index, plot_velocity in enumerate(plot_velocities):
        channel_index = int(np.argmin(np.abs(velocity_axis - plot_velocity)))
        vel_offset = velocity_axis[channel_index] - vsys
        if np.abs(vel_offset) > config.vlim:
            continue

        original_image = original_cube[channel_index]
        mirror_image = mirror_cube[channel_index]
        residual_image = residual_cube[channel_index]

        fig, axes = plt.subplots(1, 3, figsize=(25, 8))
        vmax_original = np.nanmax(original_image)
        residual_limit = np.nanmax(np.abs(original_image))

        for ax, data, title in zip(
            axes,
            (original_image, mirror_image, residual_image),
            (
                rf"Original, $v={vel_offset:.2f}\,\mathrm{{km/s}}$",
                "Mirror",
                "Residual",
            ),
        ):
            if title == "Residual":
                image = ax.imshow(
                    data,
                    origin="lower",
                    cmap="bwr",
                    vmin=-residual_limit,
                    vmax=residual_limit,
                    extent=extent,
                )
            else:
                image = ax.imshow(
                    data,
                    origin="lower",
                    cmap="inferno",
                    vmin=0,
                    vmax=vmax_original,
                    extent=extent,
                )

            ax.set_aspect("equal")
            ax.set_xlabel(r"$\Delta$RA [arcsec]")
            ax.set_ylabel(r"$\Delta$Dec [arcsec]")
            ax.set_title(title)
            ax.set_xlim(config.plot_lim, -config.plot_lim)
            ax.set_ylim(-config.plot_lim, config.plot_lim)

        divider = make_axes_locatable(axes[2])
        cax = divider.append_axes("right", size="5%", pad=0.05)
        fig.colorbar(image, cax=cax)
        plt.tight_layout()
        fig.savefig(out_path / f"v_{index:03d}_{vel_offset:.2f}km_s.pdf")
        plt.close(fig)


def generate_isosurface_html(
    source_name: str,
    source_fits: str | Path,
    mirror_dir: str | Path,
    out_dir: str | Path,
    config: HtmlConfig,
    dsharp: bool = False,
):
    paths = build_mirror_paths(source_fits, mirror_dir)
    residual_fits = resolve_generated_file(paths.residual_fits, paths.mirror_dir, "_res.fits")
    params_npy = resolve_generated_file(paths.params_npy, paths.mirror_dir, "_mirrorparams.npy")

    data_r, x_r, vel_r = mirrordisk_res_ana.preprocess(
        source_name,
        config.plot_lim,
        config.skip1,
        config.skip2,
        config.vlim,
        residual_fits,
        params_npy,
        dsharp,
    )

    x_grid, y_grid, z_grid = np.meshgrid(x_r, x_r, vel_r, indexing="ij")
    data_convert = data_r.T.astype("float64")
    vmin, vmax = np.percentile(data_convert[0], [20, 80])
    contour_value = config.contour_sigma * np.std(
        data_convert[(data_convert > vmin) & (data_convert < vmax)]
    )
    mirrordisk_res_ana.save_isosurface_html(
        x_grid,
        y_grid,
        z_grid,
        data_convert,
        contour_value,
        config.plot_lim,
        source_name,
        Path(out_dir),
    )
    return contour_value


def analyze_residuals(
    source_name: str,
    source_fits: str | Path,
    mirror_dir: str | Path,
    out_dir: str | Path,
    config: ResidualAnalysisConfig,
    dsharp: bool = False,
):
    paths = build_mirror_paths(source_fits, mirror_dir)
    output_path = Path(out_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    residual_fits = resolve_generated_file(paths.residual_fits, paths.mirror_dir, "_res.fits")
    params_npy = resolve_generated_file(paths.params_npy, paths.mirror_dir, "_mirrorparams.npy")

    data_r, x_r, vel_r = mirrordisk_res_ana.preprocess(
        source_name,
        config.plot_lim,
        config.skip1,
        config.skip2,
        config.vlim,
        residual_fits,
        params_npy,
        dsharp,
    )

    for sign, suffix, positive in ((1.0, "pos", True), (-1.0, "neg", False)):
        mask = mirrordisk_res_ana.compute_dendro_mask(
            sign * data_r,
            config.nsigma,
            config.min_npix,
        )
        masked_data = np.where(mask, sign * data_r, np.nan)
        moment0, moment1 = mirrordisk_res_ana.compute_moments(masked_data, vel_r)
        mirrordisk_res_ana.plot_moments(moment0, moment1, x_r, source_name, output_path, positive)
        moment8 = mirrordisk_res_ana.compute_moment_n(masked_data, vel_r, 8)
        moment9 = mirrordisk_res_ana.compute_moment_n(masked_data, vel_r, 9)
        map_name = f"{source_name}_{suffix}"
        mirrordisk_res_ana.plot_scalar_map(moment8, x_r, map_name, output_path, "Moment8")
        mirrordisk_res_ana.plot_scalar_map(
            moment9,
            x_r,
            map_name,
            output_path,
            "Moment9",
            cmap="bwr",
            symmetric=True,
        )


PIPELINE_STEP_NAMES = ("mirror", "channel_maps", "html", "residuals")


def build_pipeline_steps(
    source_name: str,
    source_fits: str | Path,
    mirror_dir: str | Path,
    channel_map_dir: str | Path,
    html_dir: str | Path,
    moment_dir: str | Path,
    mirror_config: MirrorProcessingConfig,
    channel_map_config: ChannelMapConfig,
    html_config: HtmlConfig,
    residual_analysis_config: ResidualAnalysisConfig,
    dsharp: bool = False,
):
    return {
        "mirror": lambda: generate_mirror_products(
            source_fits,
            mirror_dir,
            mirror_config,
        ),
        "channel_maps": lambda: generate_channel_maps(
            source_name,
            source_fits,
            mirror_dir,
            channel_map_dir,
            channel_map_config,
        ),
        "html": lambda: generate_isosurface_html(
            source_name,
            source_fits,
            mirror_dir,
            html_dir,
            html_config,
            dsharp=dsharp,
        ),
        "residuals": lambda: analyze_residuals(
            source_name,
            source_fits,
            mirror_dir,
            moment_dir,
            residual_analysis_config,
            dsharp=dsharp,
        ),
    }
