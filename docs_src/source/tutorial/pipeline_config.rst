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
   This parameter determines the spatial extent used in the mirror fitting.
   The interpolation grid is built over
   ``-inp_max <= x, y <= inp_max`` in arcsec, so it sets the half-width
   of the fitted square region on the sky.

``n_points``
   This parameter determines the spatial sampling of the fitting grid.
   It is the number of interpolation samples on each spatial axis, so
   larger values produce a finer grid for the fitting.

``vec_offsets``
   This parameter determines the velocities used in the mirror fitting.
   These velocity offsets are measured relative to ``vsys_initial``, and
   the fitting velocities are computed as ``v = vsys_initial + vec_offsets``.

``CHANNEL_MAP_PARAMS``
   Parameters for PDF channel map generation.

``dv``
   This parameter determines the velocity sampling of the channel-map
   output. Channel maps are requested at intervals of ``dv`` in km/s
   around the fitted systemic velocity.

``vlim``
   This parameter determines the total velocity range shown in the
   channel maps. The code samples channels over approximately
   ``-vlim <= v - vsys <= vlim``.

``plot_lim``
   This parameter determines the spatial field of view shown in each
   channel-map panel. The displayed axes are limited to
   ``+-plot_lim`` arcsec.

``font_size`` and ``axes_labelsize``
   These parameters determine the annotation size in the PDF figures,
   including titles and axis labels.

``HTML_PARAMS``
   Parameters for the 3D residual HTML output.

``skip1``
   This parameter determines the spatial downsampling applied before
   building the 3D residual cube. The code keeps every ``skip1``-th
   spatial pixel along both sky axes.

``skip2``
   This parameter determines the spectral downsampling applied before
   meshing. The code keeps every ``skip2``-th velocity channel.

``vlim``
   This parameter determines the velocity range retained for the 3D
   residual view. Only channels satisfying
   ``|v - vsys| < vlim`` are used.

``plot_lim``
   This parameter determines the spatial region retained for the 3D
   residual view. Only pixels satisfying
   ``|x| < plot_lim`` and ``|y| < plot_lim`` are used.

``contour_sigma``
   This parameter determines the isosurface threshold. The plotted
   contour level is computed from the measured noise as
   ``contour_sigma * sigma``.

``RESIDUAL_ANALYSIS_PARAMS``
   Parameters for residual moment-map analysis.

``skip1``
   This parameter determines the spatial downsampling used before
   residual moment analysis. The code keeps every ``skip1``-th spatial
   pixel.

``skip2``
   This parameter determines the spectral downsampling used before
   residual moment analysis. The code keeps every ``skip2``-th
   velocity channel.

``vlim``
   This parameter determines the velocity range included in the
   residual analysis. Only channels satisfying
   ``|v - vsys| < vlim`` are analyzed.

``plot_lim``
   This parameter determines the spatial region included in the
   residual analysis. Only pixels satisfying
   ``|x| < plot_lim`` and ``|y| < plot_lim`` are analyzed.

``min_npix``
   This parameter determines the minimum connected structure size
   retained by the dendrogram mask. Smaller connected residual
   features are discarded.

``nsigma``
   This parameter determines the significance threshold for the
   dendrogram mask. Residual emission must exceed approximately
   ``nsigma * sigma`` to be included.
