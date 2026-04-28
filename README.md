# mirrordisk

`mirrordisk` extracts non-axisymmetric residual structure from ALMA spectral-line cubes by comparing each channel with its mirrored counterpart across the disk minor axis.

## Install

```bash
pip install .
```
for users.  

```bash
pip install -e .
```
for developers. 

Main dependencies are listed in `setup.py` and `requirements.txt`.

## Run

The current runnable workflow is `tests/main.py`.

Run all steps:

```bash
python tests/main.py \
  --targets-csv tests/targets.csv \
  --output-root /path/to/output
```

Run one step:

```bash
python tests/main.py \
  --targets-csv tests/targets.csv \
  --output-root /path/to/output \
  mirror
```

Run one dataset only:

```bash
python tests/main.py \
  --targets-csv tests/targets.csv \
  --output-root /path/to/output \
  --dataset J1615
```

Available steps:

- `mirror`
- `channel_maps`
- `html`
- `residuals`

## Input

`--targets-csv` must include:

- `source_name`
- `source_fits_path`
- `pa_deg_initial`
- `x_cen_initial`
- `vsys_initial`

Example:

```csv
source_name,source_fits_path,pa_deg_initial,x_cen_initial,vsys_initial
J1615,/path/to/J1615_cube.fits,146,0,4.7
```

If `vsys_initial` is blank, it is estimated from the cube.

## Config

Shared defaults live in `tests/config.py`.

- `MIRROR_DEFAULT_PARAMS`
- `CHANNEL_MAP_PARAMS`
- `HTML_PARAMS`
- `RESIDUAL_ANALYSIS_PARAMS`

## Output

Given `--output-root /path/to/output`, the pipeline writes:

- `/path/to/output/result/mirror/`
- `/path/to/output/result/channel_maps/<source_name>/`
- `/path/to/output/html/`
- `/path/to/output/moms/`

## Data

Link to ALMA Large program datasets: 
- `exoALMA`: <https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/CFHWNH>
- `DSHARP`: <https://almascience.eso.org/almadata/lp/DSHARP/>
- `MAPS`: <https://alma-maps.info/data.html>

