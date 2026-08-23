# Terrain-Driven Flow Concentration vs. Reported Urban Flooding — Addis Ababa

Code accompanying the manuscript *"Terrain-Driven Flow Concentration and
Independently Reported Urban Flooding in Addis Ababa, Ethiopia: A Free-Data
Screening Evaluation"* (Independent Research Project, revised August 2026).

**Central finding:** a free-data terrain screening layer (D8 flow
accumulation on FABDEM) behaves as hydrologically expected across three
plausibility checks, but corresponds to only 1 of 10 independently reported
flood locations in Addis Ababa — a gap shown (one-sided Mann-Whitney U,
p = 0.0039) to be unlikely to arise from the city's own flow-accumulation
baseline alone. The nine terrain-missed locations show significantly
elevated land-cover-derived runoff relative to a citywide background,
consistent with a distinct, drainage-capacity-limited flood mechanism that
terrain analysis is not designed to detect.

## Repository structure

```
src/
  utils.py                              shared helpers (raster sampling, smoothing, bootstrap)
  01_dem_flow_accumulation.py           FABDEM download + D8 flow routing        (Sec 3.3-3.4, 4.1)
  02_road_sampling.py                   road-segment flow-accum sampling         (Sec 3.5)
  03_waterway_validation.py             waterway-proximity check, Table 2        (Sec 4.2)
  04_subcity_corroboration.py           sub-city classification, Table 3         (Sec 4.3)
  05_threshold_sensitivity.py           stream-threshold sensitivity, Table 4    (Sec 4.4)
  06_cn_runoff_model.py                 Curve Number + SCS-CN runoff, CHIRPS     (Sec 3.6-3.7)
  07_flood_location_inventory.py        10 named flood locations, geocoding      (Sec 3.8)
  08_terrain_correspondence_test.py     central finding: Mann-Whitney U test     (Sec 3.10, 4.6-4.7)
  09_cn_runoff_significance_test.py     CN/runoff background test + robustness   (Sec 3.10, 4.5, 3.11)
run_pipeline.py                         documents run order / dependencies between stages
data/README.md                         data source table (Table 1) + reproducibility note
archive/original_notebook_full.py      full, unedited original Colab notebook (see note below)
```

## Why there's an `archive/` folder

The analysis was developed iteratively in a single long Colab notebook,
including some abandoned approaches that are explicitly discussed as
methodological dead ends in the manuscript itself (e.g. Sec 3.10 describes
trying and rejecting a percentile-binning statistical test before landing
on the raw-value Mann-Whitney U test actually reported). The scripts in
`src/` are a cleaned-up, deduplicated distillation of that notebook,
organized to match the manuscript's own section structure.

The original notebook is preserved unedited in `archive/` for full
transparency and provenance. **Note for anyone reviewing it:** it contains
a large duplicated block (the CN/runoff background test and its sensitivity
analysis, roughly notebook Cells 40–52, appear twice back-to-back) — this
was a copy-paste artifact during development, not a second independent
analysis. `src/09_cn_runoff_significance_test.py` is the single,
deduplicated version of that logic.

## Requirements

```
pip install -r requirements.txt
```

You'll also need:
- A Google Earth Engine account/project (for FABDEM, ESA WorldCover, CHIRPS)
- Internet access (OSM/Nominatim for roads, waterways, and geocoding; geoBoundaries API for sub-city polygons)

## Reproducing the analysis

The pipeline is not a single push-button script — several stages involve
manual checkpoints in the original workflow (verifying sub-city name matches
against geoBoundaries' spelling variants, spot-checking geocoded flood
locations before running statistics on them). Run the numbered scripts in
`src/` in order, ideally in a notebook, following `run_pipeline.py`'s
documented order and I/O dependencies.

## Data availability

All datasets are freely and publicly available from their original
providers — see `data/README.md` for exact asset identifiers. No raw data
is redistributed in this repository.

## Author

Amhasilasie Mulugeta Aemero

## Citation

See `CITATION.cff` (already points to https://github.com/ami-cho/-addis-flood-screening).

## License

MIT — see `LICENSE`.
