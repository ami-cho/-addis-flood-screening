"""
Manuscript Sec 4.4: flow-accumulation threshold sensitivity (Table 4).

Important design point (Sec 4.4): testing sensitivity using only the
most extreme, top-ranked points would give a spuriously reassuring null
result, because those points exceed every tested threshold by 1-3 orders
of magnitude. This script instead selects road points whose flow
accumulation actually falls INSIDE the tested threshold range
(200-10,000), since those are the only points where changing the
threshold could possibly flip their stream/non-stream classification.
"""

import numpy as np
from scipy.ndimage import distance_transform_edt

THRESHOLDS = [200, 500, 1000, 2000, 5000, 10000]


def select_in_range_test_roads(roads_gdf, low=200, high=10000, n=15):
    candidate_roads = roads_gdf.dropna(subset=["flow_accum"])
    in_range = candidate_roads[
        (candidate_roads["flow_accum"] >= low) & (candidate_roads["flow_accum"] <= high)
    ].drop_duplicates(subset=["flow_accum"])
    print(f"Roads with flow_accum in the {low}-{high} test range: {len(in_range)}")

    test_roads = in_range.sort_values("flow_accum").iloc[
        np.linspace(0, len(in_range) - 1, min(n, len(in_range))).astype(int)
    ].copy()
    test_roads["midpoint"] = test_roads.geometry.interpolate(0.5, normalized=True)
    test_roads["lat"] = test_roads["midpoint"].y
    test_roads["lon"] = test_roads["midpoint"].x
    return test_roads


def threshold_sensitivity(acc, grid, test_roads, thresholds=THRESHOLDS):
    """Table 4: % of study area classified as stream, and % of in-range test
    roads classified 'on-stream', at each threshold."""
    acc_arr = np.asarray(acc)
    cellsize_deg = abs(grid.affine.a)
    results = []

    for thresh in thresholds:
        stream_mask = acc_arr > thresh
        pct_area = 100 * stream_mask.sum() / stream_mask.size

        dist_cells = distance_transform_edt(~stream_mask)
        dist_m = dist_cells * cellsize_deg * 111320  # deg -> m at the equator-ish latitude

        dists = []
        for _, row in test_roads.iterrows():
            col, r = ~grid.affine * (row["lon"], row["lat"])
            col, r = int(col), int(r)
            if 0 <= r < dist_m.shape[0] and 0 <= col < dist_m.shape[1]:
                dists.append(dist_m[r, col])

        pct_on_stream = 100 * sum(d == 0 for d in dists) / len(dists)
        results.append(
            {"threshold": thresh, "pct_area_stream": pct_area, "pct_test_roads_on_stream": pct_on_stream}
        )
        print(
            f"threshold={thresh}: {pct_area:.2f}% of study area is stream, "
            f"{pct_on_stream:.0f}% of test roads classified 'on stream'"
        )

    return results
