"""
Driver script showing the pipeline run order and how outputs from each
stage feed the next. This mirrors the manuscript's Sec 3-4 structure.

Each stage requires an authenticated Google Earth Engine session
(`ee.Authenticate()` on first run) and internet access (GEE, OSM/Nominatim,
geoBoundaries, CHIRPS). This will NOT run in a sandboxed/offline environment.

  01_dem_flow_accumulation.py       -> grid, acc              (Sec 3.3-3.4, 4.1)
  02_road_sampling.py               -> roads_gdf, top50        (Sec 3.5)
  03_waterway_validation.py         -> Table 2                 (Sec 4.2)
  04_subcity_corroboration.py       -> Table 3                 (Sec 4.3)
  05_threshold_sensitivity.py       -> Table 4                 (Sec 4.4)
  06_cn_runoff_model.py             -> cn_image, runoff_image  (Sec 3.6-3.7)
  07_flood_location_inventory.py    -> geocoded_locations       (Sec 3.8)
  08_terrain_correspondence_test.py -> Table 6, Sec 4.6 p-value (Sec 3.10, 4.6-4.7)
  09_cn_runoff_significance_test.py -> Table 5, Sec 4.5, 3.11   (Sec 3.10, 4.5, 3.11)

See README.md for the full narrative and archive/original_notebook_full.py
for the unedited exploratory development history this was distilled from.
"""

import sys
sys.path.insert(0, "src")

if __name__ == "__main__":
    print(__doc__)
    print(
        "This driver is documentation of run order, not a one-shot script -- "
        "each stage depends on live GEE/OSM/CHIRPS data pulls and manual "
        "checkpoints (e.g. verifying sub-city name matches, inspecting "
        "geocoding results before proceeding). Run the numbered scripts in "
        "src/ interactively (e.g. in a notebook) in the order listed above."
    )
