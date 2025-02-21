Introduction
============

pybaselines is a Python library that provides many different algorithms for
performing baseline correction on data from experimental techniques such as
Raman, FTIR, NMR, XRD, XRF, PIXE, etc. The aim of the project is to provide a
semi-unified API to allow quickly testing and comparing multiple baseline
correction algorithms to find the best one for a set of data.

pybaselines has 50+ baseline correction algorithms. Whenever possible, the original
names of the algorithms were used. The algorithms are grouped accordingly:

* Polynomial methods (:mod:`pybaselines.polynomial`)

    * poly (Regular Polynomial)
    * modpoly (Modified Polynomial)
    * imodpoly (Improved Modified Polynomial)
    * penalized_poly (Penalized Polynomial)
    * loess (Locally Estimated Scatterplot Smoothing)
    * quant_reg (Quantile Regression)
    * goldindec (Goldindec Method)

* Whittaker-smoothing-based methods (:mod:`pybaselines.whittaker`)

    * asls (Asymmetric Least Squares)
    * iasls (Improved Asymmetric Least Squares)
    * airpls (Adaptive Iteratively Reweighted Penalized Least Squares)
    * arpls (Asymmetrically Reweighted Penalized Least Squares)
    * drpls (Doubly Reweighted Penalized Least Squares)
    * iarpls (Improved Asymmetrically Reweighted Penalized Least Squares)
    * aspls (Adaptive Smoothness Penalized Least Squares)
    * psalsa (Peaked Signal's Asymmetric Least Squares Algorithm)
    * derpsalsa (Derivative Peak-Screening Asymmetric Least Squares Algorithm)
    * brpls (Bayesian Reweighted Penalized Least Squares)
    * lsrpls (Locally Symmetric Reweighted Penalized Least Squares)

* Morphological methods (:mod:`pybaselines.morphological`)

    * mpls (Morphological Penalized Least Squares)
    * mor (Morphological)
    * imor (Improved Morphological)
    * mormol (Morphological and Mollified Baseline)
    * amormol (Averaging Morphological and Mollified Baseline)
    * rolling_ball (Rolling Ball Baseline)
    * mwmv (Moving Window Minimum Value)
    * tophat (Top-hat Transformation)
    * mpspline (Morphology-Based Penalized Spline)
    * jbcd (Joint Baseline Correction and Denoising)

* Spline methods (:mod:`pybaselines.spline`)

    * mixture_model (Mixture Model)
    * irsqr (Iterative Reweighted Spline Quantile Regression)
    * corner_cutting (Corner-Cutting Method)
    * pspline_asls (Penalized Spline Version of asls)
    * pspline_iasls (Penalized Spline Version of iasls)
    * pspline_airpls (Penalized Spline Version of airpls)
    * pspline_arpls (Penalized Spline Version of arpls)
    * pspline_drpls (Penalized Spline Version of drpls)
    * pspline_iarpls (Penalized Spline Version of iarpls)
    * pspline_aspls (Penalized Spline Version of aspls)
    * pspline_psalsa (Penalized Spline Version of psalsa)
    * pspline_derpsalsa (Penalized Spline Version of derpsalsa)
    * pspline_brpls (Penalized Spline Version of brpls)
    * pspline_lsrpls (Penalized Spline Version of lsrpls)

* Smoothing-based methods (:mod:`pybaselines.smooth`)

    * noise_median (Noise Median method)
    * snip (Statistics-sensitive Non-linear Iterative Peak-clipping)
    * swima (Small-Window Moving Average)
    * ipsa (Iterative Polynomial Smoothing Algorithm)
    * ria (Range Independent Algorithm)

* Baseline/Peak Classification methods (:mod:`pybaselines.classification`)

    * dietrich (Dietrich's Classification Method)
    * golotvin (Golotvin's Classification Method)
    * std_distribution (Standard Deviation Distribution)
    * fastchrom (FastChrom's Baseline Method)
    * cwt_br (Continuous Wavelet Transform Baseline Recognition)
    * fabc (Fully Automatic Baseline Correction)
    * rubberband (Rubberband Method)

* Optimizers (:mod:`pybaselines.optimizers`)

    * collab_pls (Collaborative Penalized Least Squares)
    * optimize_extended_range
    * adaptive_minmax (Adaptive MinMax)
    * custom_bc (Customized Baseline Correction)

* Miscellaneous methods (:mod:`pybaselines.misc`)

    * interp_pts (Interpolation between points)
    * beads (Baseline Estimation And Denoising with Sparsity)
