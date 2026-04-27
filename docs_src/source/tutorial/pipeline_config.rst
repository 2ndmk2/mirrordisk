Pipeline Config
================

The ``tests2/main.py`` entry point reads target-specific parameters from a CSV file
and combines them with common plotting and fitting defaults defined in
``tests2/config.py``.

Running the pipeline
--------------------

Use ``--targets-csv`` to specify the target table and ``--output-root`` to choose
where generated files are written.

.. code:: bash

   PYTHONPATH=src python tests2/main.py \
     --targets-csv "/path/to/targets.csv" \
     --output-root "/path/to/output" \
     --dataset J1615 \
     mirror

If ``--dataset`` is omitted, every row in the CSV is processed in order.

Target table
------------

The target CSV must include the following columns:

.. list-table::
   :header-rows: 1

   * - Column
     - Meaning
   * - ``source_name``
     - Target identifier used for dataset selection and output subdirectories.
   * - ``source_fits_path``
     - Full path to the input FITS cube.
   * - ``pa_deg_initial``
     - Initial position angle in degrees for the mirror fitting.
   * - ``x_cen_initial``
     - Initial center offset in arcsec along the fitted symmetry-axis intercept.
   * - ``vsys_initial``
     - Initial systemic velocity in km/s. Leave blank to estimate it from the cube.

Example:

.. code:: text

   source_name,source_fits_path,pa_deg_initial,x_cen_initial,vsys_initial
   J1615,/Volumes/T7 Shield/exoalma_for_code/J1615_12CO_high-res.image.fits,142.0,0.0,

Common parameters in ``tests2/config.py``
-----------------------------------------

``MIRROR_DEFAULT_PARAMS``
   Shared defaults for the mirror fitting stage.

``inp_max``
   Half-width of the interpolation grid in arcsec.

``n_points``
   Number of interpolation samples per spatial axis.

``vec_offsets``
   Velocity offsets in km/s, measured relative to ``vsys_initial``.

``CHANNEL_MAP_PARAMS``
   Parameters for PDF channel map generation.

``dv``
   Velocity spacing between plotted channels in km/s.

``vlim``
   Maximum absolute velocity offset from systemic velocity used in plots.

``plot_lim``
   Spatial plot half-width in arcsec.

``font_size`` and ``axes_labelsize``
   Matplotlib font sizes for labels and titles.

``HTML_PARAMS``
   Parameters for the 3D residual HTML output.

``skip1``
   Spatial downsampling factor.

``skip2``
   Spectral downsampling factor.

``plot_lim``
   Spatial half-width in arcsec used before meshing the cube.

``contour_sigma``
   Multiplicative factor used to set the isosurface threshold from the measured noise.

``RESIDUAL_ANALYSIS_PARAMS``
   Parameters for residual moment-map analysis.

``min_npix``
   Minimum connected voxel count retained by the dendrogram mask.

``nsigma``
   Signal threshold, in noise sigma, used when constructing the mask.

``skip1``, ``skip2``, ``vlim``, and ``plot_lim``
   Applied in the same way as in ``HTML_PARAMS`` before computing moments.

