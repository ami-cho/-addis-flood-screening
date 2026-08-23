"""
Shared helper functions used across the pipeline scripts.

These are extracted (and lightly cleaned up / deduplicated) from the
original exploratory Colab notebook -- see archive/original_notebook_full.py
for the full, unedited development history.
"""

import numpy as np
import rasterio
import rasterio.transform
from scipy.ndimage import uniform_filter


def cn_to_runoff(cn_val, p):
    """
    SCS Curve Number runoff depth (Eq. 1 in the manuscript, Sec 3.6).

    Q = (P - 0.2S)^2 / (P + 0.8S), for P > 0.2S; Q = 0 otherwise
    S = 25400 / CN - 254   (mm)
    """
    if cn_val <= 0:
        return 0.0
    s = (25400 / cn_val) - 254
    if p <= 0.2 * s:
        return 0.0
    return ((p - 0.2 * s) ** 2) / (p + 0.8 * s)


def sample_raster(tif_path, lonlat_list):
    """Sample a single-band local raster at a list of (lon, lat) points."""
    with rasterio.open(tif_path) as src:
        band = src.read(1)
        nodata = src.nodata
        vals = []
        for lon, lat in lonlat_list:
            row, col = src.index(lon, lat)
            if 0 <= row < band.shape[0] and 0 <= col < band.shape[1]:
                v = band[row, col]
                if nodata is not None and v == nodata:
                    v = np.nan
                vals.append(v)
            else:
                vals.append(np.nan)
    return np.array(vals, dtype=float)


def load_raster_array(tif_path):
    """Load a single-band raster to a float array (NaN for nodata) + its transform."""
    with rasterio.open(tif_path) as src:
        arr = src.read(1).astype(float)
        if src.nodata is not None:
            arr[arr == src.nodata] = np.nan
        transform = src.transform
    return arr, transform


def smooth_array(arr, buffer_m, pixel_scale):
    """
    NaN-aware moving-average smoother, radius chosen to approximate a
    buffer_m-radius buffer at the given pixel_scale (meters/pixel).

    Manuscript Sec 3.6 / 4.5: runoff is smoothed directly (not CN-then-
    recompute-runoff), because Eq. 1 is nonlinear in CN and averaging the
    nonlinear output is the statistically correct order of operations
    (Jensen's inequality).
    """
    radius_px = max(1, int(round(buffer_m / pixel_scale)))
    size = 2 * radius_px + 1
    valid = ~np.isnan(arr)
    arr_filled = np.where(valid, arr, 0.0)
    sum_smoothed = uniform_filter(arr_filled, size=size, mode="nearest")
    count_smoothed = uniform_filter(valid.astype(float), size=size, mode="nearest")
    with np.errstate(invalid="ignore", divide="ignore"):
        smoothed = sum_smoothed / count_smoothed
    smoothed[count_smoothed == 0] = np.nan
    return smoothed


def sample_array_at_points(arr, transform, lonlat_list):
    """Sample an in-memory raster array (with its affine transform) at (lon, lat) points."""
    vals = []
    for lon, lat in lonlat_list:
        row, col = rasterio.transform.rowcol(transform, lon, lat)
        if 0 <= row < arr.shape[0] and 0 <= col < arr.shape[1]:
            vals.append(arr[row, col])
        else:
            vals.append(np.nan)
    return np.array(vals, dtype=float)


def prob_superiority(a, b):
    """Effect size: P(a > b) for two independent samples, via Mann-Whitney U.
    0.5 = no difference; 1.0 = complete separation (every a exceeds every b)."""
    from scipy.stats import mannwhitneyu
    u, _ = mannwhitneyu(a, b, alternative="greater")
    return u / (len(a) * len(b))


def bootstrap_effect_size_ci(named_vals, bg_vals, n_boot=10000, seed=42, ci=95):
    """Bootstrap CI on the probability-of-superiority effect size, resampling
    the (small, fixed) named-location values -- see manuscript Sec 3.10."""
    rng = np.random.default_rng(seed)
    n_named = len(named_vals)
    n_bg = len(bg_vals)
    boot_effects = np.empty(n_boot)
    for i in range(n_boot):
        named_sample = rng.choice(named_vals, size=n_named, replace=True)
        bg_sample = rng.choice(bg_vals, size=n_bg, replace=True)
        boot_effects[i] = prob_superiority(named_sample, bg_sample)
    lower = np.percentile(boot_effects, (100 - ci) / 2)
    upper = np.percentile(boot_effects, 100 - (100 - ci) / 2)
    point = prob_superiority(named_vals, bg_vals)
    return point, lower, upper, boot_effects
