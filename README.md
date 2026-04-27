# mirrordisk

`mirrordisk` is a Python package for extracting non-axisymmetric residual structure from ALMA spectral-line cubes by comparing each channel with its mirrored counterpart across the disk minor axis.

This README describes the current runnable workflow based on `tests/`.

## Overview

The `tests` pipeline does the following:

Common CLI options for every step:

- `--targets-csv`: choose the target table
- `--output-root`: choose the output base directory
- `--dataset`: run one dataset only

1. Fit mirror-symmetry parameters and generate mirrored and residual FITS cubes.
   Step: `mirror`
   Config: `MIRROR_DEFAULT_PARAMS` plus target CSV columns `pa_deg_initial`, `x_cen_initial`, `vsys_initial`
2. Create per-channel PDF comparison plots from the original, mirrored, and residual cubes.
   Step: `channel_maps`
   Config: `CHANNEL_MAP_PARAMS`
3. Build an interactive 3D residual isosurface HTML.
   Step: `html`
   Config: `HTML_PARAMS`
4. Produce residual moment maps and higher-order scalar maps.
   Step: `residuals`
   Config: `RESIDUAL_ANALYSIS_PARAMS`

The main file is `tests/main.py`, and its behavior is configured by `tests/config.py` and a target CSV table.

## Installation

Basic install:

```bash
pip install .
```

Editable install:

```bash
pip install -e .
```

## Runtime dependencies

The default `tests` pipeline requires:

- `numpy`
- `scipy`
- `astropy`
- `matplotlib`
- `plotly`
- `pandas`
- `psutil`
- `astrodendro`

They are listed in `setup.py` and `requirements.txt`.

JAX-backed modules are optional. The default pipeline does not require JAX.

## Quick start

Run one step:

```bash
python tests/main.py \
  --targets-csv tests/targets.csv \
  --output-root /path/to/output \
  mirror
```

Run all steps for all datasets listed in the CSV:

```bash
python tests/main.py \
  --targets-csv tests/targets.csv \
  --output-root /path/to/output
```

Run one dataset only when needed:

```bash
python tests/main.py \
  --targets-csv tests/targets.csv \
  --output-root /path/to/output \
  --dataset J1615
```

If no step is given, all steps run in this order:

- `mirror`
- `channel_maps`
- `html`
- `residuals`

## Target CSV format

The target table must include these columns:

- `source_name`: dataset identifier used by `--dataset` and output naming.
- `source_fits_path`: full path to the input FITS cube.
- `pa_deg_initial`: initial position angle in degrees.
- `x_cen_initial`: initial center offset in arcsec.
- `vsys_initial`: initial systemic velocity in km/s. Leave blank to estimate it from the cube.

Example:

```csv
source_name,source_fits_path,pa_deg_initial,x_cen_initial,vsys_initial
J1615,/path/to/J1615_cube.fits,146,0,4.7
```

The repository example lives at `tests/targets.csv`.

## Output structure

Given `--output-root /path/to/output`, the pipeline writes:

- `/path/to/output/result/mirror/`: fitted parameters, mirrored FITS, residual FITS
- `/path/to/output/result/channel_maps/<source_name>/`: channel-by-channel PDF figures
- `/path/to/output/html/`: interactive residual isosurface HTML
- `/path/to/output/moms/`: moment maps and higher-order residual maps

Mirror products are named from the input FITS stem:

- `<stem>_mirrorparams.npy`
- `<stem>_mirror.fits`
- `<stem>_res.fits`

## Configuration in `tests/config.py`

`tests/config.py` combines target-specific CSV values with shared defaults.

### Mirror fitting

`MIRROR_DEFAULT_PARAMS`:

- `inp_max`: half-width of the interpolation grid in arcsec
- `n_points`: number of interpolation samples per spatial axis
- `vec_offsets`: velocity offsets in km/s relative to `vsys_initial`

### Channel maps

`CHANNEL_MAP_PARAMS`:

- `dv`: velocity spacing in km/s between plotted channels
- `vlim`: maximum absolute velocity offset from systemic velocity
- `plot_lim`: spatial half-width in arcsec
- `font_size`, `axes_labelsize`: matplotlib font sizes

### 3D HTML residual view

`HTML_PARAMS`:

- `skip1`: spatial downsampling factor
- `skip2`: spectral downsampling factor
- `vlim`: velocity range used before meshing
- `plot_lim`: spatial limit used before meshing
- `contour_sigma`: multiplier used to set the isosurface threshold

### Residual analysis

`RESIDUAL_ANALYSIS_PARAMS`:

- `skip1`, `skip2`, `vlim`, `plot_lim`: preprocessing controls
- `min_npix`: minimum connected voxel count for the dendrogram mask
- `nsigma`: significance threshold in noise sigma

## Step details

`mirror`

- Fits mirror-symmetry parameters.
- Writes optimized parameters and generates mirrored and residual FITS cubes.

`channel_maps`

- Loads the original, mirrored, and residual cubes.
- Writes one PDF per sampled velocity channel with side-by-side panels.

`html`

- Builds an interactive 3D isosurface view from the residual cube.
- Writes an HTML file under the HTML output directory.

`residuals`

- Masks significant residual structure with `astrodendro`.
- Produces positive and negative residual moment maps.
- Produces additional scalar maps for moment 8 and moment 9.

## Notes

- The examples assume `pip install .` or `pip install -e .` has already been run, so `PYTHONPATH=src` is not needed.
- `--dataset` is optional. If omitted, every row in the CSV is processed.
- The current examples assume local FITS paths; the repository does not bundle the data cubes.
- If `vsys_initial` is blank in the CSV, the code estimates the systemic velocity from the cube.
