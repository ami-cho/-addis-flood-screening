"""
Manuscript Sec 3.10 / 4.5 / 3.11: CN and runoff at the 10 named flood
locations vs. a citywide background, with the sensitivity/robustness
analysis reported in the manuscript.

DEDUPLICATION NOTE: the original exploratory notebook (see
archive/original_notebook_full.py) pasted this entire block in twice
(an "ADDENDUM" that got added to the notebook a second time by mistake).
This script is the single, cleaned-up version of that logic. The
manuscript's reported numbers (Table 5, Sec 4.5, Sec 3.11) come from the
"buffer-smoothed, city-boundary-restricted" scenario specifically --
see `run_full_robustness_suite()` below for why the other three scenarios
exist and why that one is the defensible primary result.
"""

import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu

from utils import (
    sample_raster,
    load_raster_array,
    smooth_array,
    sample_array_at_points,
    bootstrap_effect_size_ci,
)

BUFFER_M = 300       # matches the 300m buffer used for individual points (Sec 3.6)
EXPORT_SCALE = 30    # matches the flow-accumulation grid resolution


def run_cn_runoff_test(cn_source, runoff_source, named_pts, bg_pts, label="",
                        from_arrays=False, cn_transform=None, q_transform=None):
    """
    One-sided Mann-Whitney U test: named-location CN/runoff > background.
    Set from_arrays=True to sample from in-memory (possibly smoothed) arrays
    instead of re-reading from disk each call.
    """
    if from_arrays:
        named_cn = sample_array_at_points(cn_source, cn_transform, named_pts)
        bg_cn = sample_array_at_points(cn_source, cn_transform, bg_pts)
        named_q = sample_array_at_points(runoff_source, q_transform, named_pts)
        bg_q = sample_array_at_points(runoff_source, q_transform, bg_pts)
    else:
        named_cn = sample_raster(cn_source, named_pts)
        bg_cn = sample_raster(cn_source, bg_pts)
        named_q = sample_raster(runoff_source, named_pts)
        bg_q = sample_raster(runoff_source, bg_pts)

    named_cn, bg_cn = named_cn[~np.isnan(named_cn)], bg_cn[~np.isnan(bg_cn)]
    named_q, bg_q = named_q[~np.isnan(named_q)], bg_q[~np.isnan(bg_q)]

    u_cn, p_cn = mannwhitneyu(named_cn, bg_cn, alternative="greater")
    u_q, p_q = mannwhitneyu(named_q, bg_q, alternative="greater")
    eff_cn = u_cn / (len(named_cn) * len(bg_cn))
    eff_q = u_q / (len(named_q) * len(bg_q))

    print(f"\n=== {label} ===")
    print(f"n named={len(named_cn)}, n background={len(bg_cn)}")
    print(f"CN     -- named median={np.median(named_cn):.1f}, bg median={np.median(bg_cn):.1f}, "
          f"p={p_cn:.4f}, effect size={eff_cn:.3f}")
    print(f"Runoff -- named median={np.median(named_q):.2f}mm, bg median={np.median(bg_q):.2f}mm, "
          f"p={p_q:.4f}, effect size={eff_q:.3f}")

    return {"p_cn": p_cn, "p_q": p_q, "eff_cn": eff_cn, "eff_q": eff_q,
            "named_cn": named_cn, "bg_cn": bg_cn, "named_q": named_q, "bg_q": bg_q}


def filter_points_in_boundary(lonlat_list, boundary):
    from shapely.geometry import Point
    return [(lon, lat) for lon, lat in lonlat_list if boundary.contains(Point(lon, lat))]


def run_full_robustness_suite(cn_tif, runoff_tif, named_lonlat, background_lonlat,
                               city_boundary):
    """
    Runs all four background/smoothing combinations reported in the
    manuscript's robustness summary (Sec 4.5):

      1. Raw pixel,      full-AOI background      -- naive first pass
      2. Buffer-smoothed, full-AOI background      -- fixes single-pixel sampling noise
      3. Raw pixel,      city-boundary background  -- fixes rural/urban confound
      4. Buffer-smoothed, city-boundary background -- PRIMARY / reported result

    Why smoothing matters: raw single-pixel sampling put 9/10 named
    locations on exactly CN=88.0 (one built-up pixel each) rather than a
    blended neighborhood value.

    Why the city-boundary restriction matters: the flow-accumulation study
    area (Sec 2) deliberately extends beyond the administrative city to
    avoid truncating upstream catchments. That's correct for flow routing,
    but CN/runoff directly encode land cover -- comparing 10 urban addresses
    against a background that includes farmland and forested hills outside
    the city risks just re-detecting "the city is more built-up than the
    countryside" rather than testing the actual hypothesis.
    """
    cn_arr, cn_transform = load_raster_array(cn_tif)
    q_arr, q_transform = load_raster_array(runoff_tif)
    cn_smoothed = smooth_array(cn_arr, BUFFER_M, EXPORT_SCALE)
    q_smoothed = smooth_array(q_arr, BUFFER_M, EXPORT_SCALE)

    background_lonlat_city = filter_points_in_boundary(background_lonlat, city_boundary)
    print(f"Background points inside administrative city boundary: "
          f"{len(background_lonlat_city)} of {len(background_lonlat)}")
    if len(background_lonlat_city) < 200:
        print("WARNING: city-restricted background sample is small.")

    raw_full = run_cn_runoff_test(cn_arr, q_arr, named_lonlat, background_lonlat,
                                   label="Raw pixel, full-AOI background",
                                   from_arrays=True, cn_transform=cn_transform, q_transform=q_transform)
    smoothed_full = run_cn_runoff_test(cn_smoothed, q_smoothed, named_lonlat, background_lonlat,
                                        label=f"Buffer-smoothed ({BUFFER_M}m), full-AOI background",
                                        from_arrays=True, cn_transform=cn_transform, q_transform=q_transform)
    raw_city = run_cn_runoff_test(cn_arr, q_arr, named_lonlat, background_lonlat_city,
                                   label="Raw pixel, city-boundary-restricted background",
                                   from_arrays=True, cn_transform=cn_transform, q_transform=q_transform)
    smoothed_city = run_cn_runoff_test(cn_smoothed, q_smoothed, named_lonlat, background_lonlat_city,
                                        label=f"Buffer-smoothed ({BUFFER_M}m), city-boundary-restricted background [PRIMARY]",
                                        from_arrays=True, cn_transform=cn_transform, q_transform=q_transform)

    summary = pd.DataFrame([
        ("Raw pixel, full-AOI background", raw_full["p_cn"], raw_full["p_q"], raw_full["eff_cn"], raw_full["eff_q"]),
        ("Buffer-smoothed, full-AOI background", smoothed_full["p_cn"], smoothed_full["p_q"], smoothed_full["eff_cn"], smoothed_full["eff_q"]),
        ("Raw pixel, city-only background", raw_city["p_cn"], raw_city["p_q"], raw_city["eff_cn"], raw_city["eff_q"]),
        ("Buffer-smoothed, city-only background [PRIMARY]", smoothed_city["p_cn"], smoothed_city["p_q"], smoothed_city["eff_cn"], smoothed_city["eff_q"]),
    ], columns=["Scenario", "p_CN", "p_runoff", "effect_size_CN", "effect_size_runoff"])

    print("\n=== Final CN/Runoff Robustness Summary ===")
    print(summary.to_string(index=False))

    return {
        "raw_full": raw_full, "smoothed_full": smoothed_full,
        "raw_city": raw_city, "smoothed_city": smoothed_city,
        "summary_table": summary,
        "cn_smoothed": cn_smoothed, "q_smoothed": q_smoothed,
        "cn_transform": cn_transform, "q_transform": q_transform,
        "background_lonlat_city": background_lonlat_city,
    }


def run_bootstrap_ci(primary_result_arrays):
    """Sec 4.5: bootstrap 95% CI on the effect size, using the corrected
    (buffer-smoothed, city-restricted) sample. Report as 'uncertainty in the
    estimate given these 10 points' -- not as equivalent to a larger sample."""
    named_cn = primary_result_arrays["named_cn"]
    bg_cn = primary_result_arrays["bg_cn"]
    named_q = primary_result_arrays["named_q"]
    bg_q = primary_result_arrays["bg_q"]

    pt_cn, lo_cn, hi_cn, _ = bootstrap_effect_size_ci(named_cn, bg_cn)
    pt_q, lo_q, hi_q, _ = bootstrap_effect_size_ci(named_q, bg_q)

    print("=== Bootstrap 95% CI on effect size (smoothed, city-restricted) ===")
    print(f"CN     effect size: {pt_cn:.3f}  [95% CI: {lo_cn:.3f}, {hi_cn:.3f}]")
    print(f"Runoff effect size: {pt_q:.3f}  [95% CI: {lo_q:.3f}, {hi_q:.3f}]")
    print("Reference: 0.5 = no difference from background, 1.0 = complete separation.")

    return pd.DataFrame([
        ("CN", pt_cn, lo_cn, hi_cn),
        ("Runoff", pt_q, lo_q, hi_q),
    ], columns=["Metric", "Effect size (point est.)", "95% CI lower", "95% CI upper"])
