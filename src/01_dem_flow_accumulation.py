"""
Manuscript Sec 3.2-3.4 / 4.1: FABDEM download, hydrologic conditioning,
and D8 flow accumulation.

Requires: an authenticated Google Earth Engine project (`ee.Authenticate()`
will open a browser login the first time). Produces `addis_fabdem.tif` and,
via pysheds, an in-memory flow-accumulation grid used by later scripts.
"""

import ee
import numpy as np
import matplotlib.pyplot as plt
from pysheds.grid import Grid

# ---- Study area: bounding box of ~38.60-38.95 E, 8.80-9.10 N (Sec 2) ----
AOI = ee.Geometry.Rectangle([38.60, 8.80, 38.95, 9.10])
FABDEM_TIF = "addis_fabdem.tif"


def download_fabdem(project_id):
    ee.Authenticate()
    ee.Initialize(project=project_id)

    fabdem = ee.ImageCollection("projects/sat-io/open-datasets/FABDEM").mosaic().clip(AOI)

    stats = fabdem.reduceRegion(
        reducer=ee.Reducer.minMax(), geometry=AOI, scale=30, maxPixels=1e9
    ).getInfo()
    print("FABDEM elevation range over study area:", stats)

    import geemap
    geemap.ee_export_image(fabdem, filename=FABDEM_TIF, scale=30, region=AOI, file_per_band=False)
    return fabdem


def compute_flow_accumulation(dem_path=FABDEM_TIF):
    """
    Hydrologic conditioning + D8 flow routing (Sec 3.3-3.4).

    Real terrain has "pits" (single low pixels) and "depressions" (bigger
    sinks) that would trap water unrealistically -- these three steps fix
    that so water can flow all the way through the DEM.
    """
    grid = Grid.from_raster(dem_path)
    dem = grid.read_raster(dem_path)

    pit_filled_dem = grid.fill_pits(dem)
    flooded_dem = grid.fill_depressions(pit_filled_dem)
    inflated_dem = grid.resolve_flats(flooded_dem)

    fdir = grid.flowdir(inflated_dem)   # D8: 8 possible flow directions per cell
    acc = grid.accumulation(fdir)       # upstream cell count per pixel

    print("Flow accumulation computed. Max accumulation:", acc.max())
    return grid, acc


def plot_flow_accumulation(grid, acc, out_path="outputs/flow_accumulation.png"):
    fig, ax = plt.subplots(figsize=(10, 10))
    im = ax.imshow(np.log1p(acc), cmap="cubehelix", extent=grid.extent, zorder=2)
    plt.colorbar(im, ax=ax, label="Flow accumulation (log scale)")
    plt.title("Flow Accumulation — Addis Ababa")
    plt.savefig(out_path, dpi=200, bbox_inches="tight")
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    # Replace with your own GEE project id
    download_fabdem(project_id="addis-flood-mapping")
    grid, acc = compute_flow_accumulation()
    plot_flow_accumulation(grid, acc)
