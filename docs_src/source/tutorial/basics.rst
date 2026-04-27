Basics 
=================
When a disk velocity distribution has a rotational symmetry (e.g., Keplerian rotation for axisymetric disc), 
we expect

.. math::

   I(v, x, y) = I(2v_{\rm sys} - v, x_{\rm sym}, y_{\rm sym} ), 

where :math:`(x_{\rm sym}, y_{\rm sym})` is reflection of :math:`(x, y)` across the minor axis of the disk,     
:math:`v`  is a velocity at a channel, and :math:`v_{\rm sys}` is the system velocity. 
The line of the disk minor axis is specified by two parameters, the disk position angle PA and x or y intercept. 

If there is any non-axisymmetric perturbation that breaks the symetry, the signal should appear as the difference

.. math::

   \Delta I (v, x, y)= I(v, x, y) - I(2v_{\rm sys} - v, x_{\rm sym}, y_{\rm sym} ). 

Using observed image :math:`I(v, x, y)` and opposite-velocity image :math:`I(2v_{\rm sys} - v, x_{\rm sym}, y_{\rm sym} )` made by interpolation,
we can estimate :math:`\Delta I (v, x, y)` from observations. 

This code implements this concept to study weak planetary perturbations. 