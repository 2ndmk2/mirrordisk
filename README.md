# mirrordisk

`mirrordisk` is a Python package for extracting non-axisymmetric residual structure from ALMA spectral-line cubes by comparing each channel with its mirrored counterpart across the disk minor axis.

This README describes the current runnable workflow based on `tests/`.

## Overview

The `tests` pipeline does the following:

1. Fits mirror-symmetry parameters for a FITS cube.
2. Generates mirrored and residual FITS cubes.
3. Creates per-channel PDF comparison plots.
4. Builds an interactive 3D residual isosurface HTML.
5. Produces residual moment maps and higher-order scalar maps.

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

`setup.py` lists only part of the required stack. The `tests` pipeline imports these packages at runtime:

- `numpy`
- `scipy`
- `astropy`
- `matplotlib`
- `plotly`
- `pandas`
- `psutil`
- `astrodendro`

Install them in your environment before running the pipeline.

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

## CLI arguments

`tests/main.py` accepts:

- `--dataset`: dataset name from the target CSV. If omitted, every dataset in the CSV is processed.
- `--output-root`: base output directory.
- `--targets-csv`: CSV file defining input FITS cubes and initial parameters.
- `steps`: optional positional list chosen from `mirror`, `channel_maps`, `html`, `residuals`.

Important: `tests/config.py` sets `DEFAULT_OUTPUT_ROOT` to `/Volumes/T7 Shield/exoalma_for_code/output`. In most environments you should override this with `--output-root`.

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
