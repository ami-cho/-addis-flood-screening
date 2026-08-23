"""
Manuscript Sec 3.10 / 4.6 / 4.7: the paper's central, best-supported finding.

Compares raw flow-accumulation values at the 10 named flood locations
against 10,000 randomly sampled citywide points, using a one-sided
Mann-Whitney U test.

IMPORTANT (Sec 3.10): an earlier percentile-binning approach was tried and
abandoned -- flow accumulation is extremely right-skewed and discretized at
low values, so percentile-tie boundaries could flip the "miss rate" between
60% and 90% with no change in the underlying data. Raw-value Mann-Whitney U
avoids this artifact entirely and is the only test reported in the
manuscript.
"""

import numpy as np
from scipy.stats import mannwhitneyu


def sample_random_citywide_points(acc, n_samples=10000, seed=42):
    """Draw n_samples random points from valid (non-zero) flow-accumulation cells."""
    acc_arr = np.asarray(acc)
    valid_mask = acc_arr > 0
    valid_rows, valid_cols = np.where(valid_mask)

    rng = np.random.default_rng(seed)
    sample_idx = rng.choice(len(valid_rows), size=n_samples, replace=True)
    return valid_rows, valid_cols, sample_idx


def flow_accum_percentile(acc_arr, value):
    """Percentile of `value` within the full citywide flow-accumulation distribution."""
    return 100 * (acc_arr < value).sum() / acc_arr.size


def named_location_flow_accum(geocoded_locations, grid, acc):
    """Sample raw flow accumulation (and its citywide percentile) at each
    named flood location -- basis for Table 6."""
    acc_arr = np.asarray(acc)
    results = {}
    for label, (lat, lon) in geocoded_locations.items():
        col, r = ~grid.affine * (lon, lat)
        col, r = int(col), int(r)
        if 0 <= r < acc_arr.shape[0] and 0 <= col < acc_arr.shape[1]:
            val = acc_arr[r, col]
            pct = flow_accum_percentile(acc_arr, val)
            results[label] = {"flow_accum": val, "percentile": pct}
            print(f"{label}: flow_accum={val:.0f} ({pct:.1f}th percentile)")
        else:
            print(f"{label}: outside study area bounds")
    return results


def terrain_correspondence_test(named_raw_values, acc, n_random=10000, seed=42):
    """
    The manuscript's central statistical test (Sec 4.6):
    H0: named-location flow accumulation is drawn from the same distribution
        as random citywide flow accumulation.
    H1 (one-sided): named-location values are systematically lower.
    """
    acc_arr = np.asarray(acc)
    valid_rows, valid_cols, sample_idx = sample_random_citywide_points(acc, n_random, seed)
    random_raw_values = acc_arr[valid_rows[sample_idx], valid_cols[sample_idx]]

    stat, p_value = mannwhitneyu(named_raw_values, random_raw_values, alternative="less")

    print(f"\nMedian flow_accum -- named locations: {np.median(named_raw_values):.1f}")
    print(f"Median flow_accum -- random citywide sample: {np.median(random_raw_values):.1f}")
    print(f"Mann-Whitney U test (named < random, one-sided): p = {p_value:.4f}")

    return {
        "p_value": p_value,
        "named_median": float(np.median(named_raw_values)),
        "random_median": float(np.median(random_raw_values)),
        "random_raw_values": random_raw_values,
        "valid_rows": valid_rows,
        "valid_cols": valid_cols,
        "sample_idx": sample_idx,
    }
