"""
Manuscript Sec 3.5: road-segment flow-accumulation sampling.

The complete Addis Ababa drivable road network (OSM, via osmnx) is used,
with flow accumulation sampled at each segment's midpoint to produce a
citywide ranking. NOTE (Sec 3.5): this midpoint-sampling approach can
produce multiple highly-ranked points that are repeated samples of the
same corridor rather than independent drainage crossings -- see Fig. 1 /
Table 2, where ranks 4-9 form a single contiguous Ring Road corridor.
"""

import numpy as np
import osmnx as ox


PLACE = "Addis Ababa, Ethiopia"


def download_roads():
    roads = ox.graph_from_place(PLACE, network_type="drive")
    print(f"Roads downloaded: {len(roads.edges)} road segments")
    return roads


def sample_flow_accumulation_at_roads(roads, acc, grid):
    """Sample flow accumulation at each road segment's midpoint."""
    roads_gdf = ox.graph_to_gdfs(roads, nodes=False, edges=True)
    roads_gdf = roads_gdf.to_crs(grid.crs)

    def get_accumulation_at_point(row):
        midpoint = row.geometry.interpolate(0.5, normalized=True)
        col, r = ~grid.affine * (midpoint.x, midpoint.y)
        col, r = int(col), int(r)
        if 0 <= r < acc.shape[0] and 0 <= col < acc.shape[1]:
            return acc[r, col]
        return np.nan

    roads_gdf["flow_accum"] = roads_gdf.apply(get_accumulation_at_point, axis=1)
    roads_gdf["midpoint"] = roads_gdf.geometry.interpolate(0.5, normalized=True)
    roads_gdf["lat"] = roads_gdf["midpoint"].y
    roads_gdf["lon"] = roads_gdf["midpoint"].x
    return roads_gdf


def top_n_points(roads_gdf, n=50):
    """Table 2 / Table 3 basis: top-N flow-accumulation road points, deduplicated
    by exact flow_accum value (adjacent segments on the same corridor commonly
    share a value -- see Sec 3.5 caveat)."""
    ranked = roads_gdf.dropna(subset=["flow_accum"]).sort_values("flow_accum", ascending=False)
    return ranked.drop_duplicates(subset=["flow_accum"]).head(n)


if __name__ == "__main__":
    # Requires `grid` and `acc` from 01_dem_flow_accumulation.py
    raise SystemExit(
        "Run via the pipeline notebook/driver: this module expects `grid` and "
        "`acc` produced by 01_dem_flow_accumulation.py."
    )
