# Data Sources

No raw data files are stored in this repository — everything is pulled live
from free, public sources at run time. This mirrors Table 1 in the manuscript.

| Dataset | Source / Asset ID | Resolution | Access |
|---|---|---|---|
| FABDEM | `projects/sat-io/open-datasets/FABDEM` (GEE community catalog) | 30 m | Google Earth Engine |
| OSM road network | via `osmnx` | vector | OpenStreetMap |
| OSM waterways | via `osmnx` (148 features used in the manuscript) | vector | OpenStreetMap |
| ESA WorldCover | `ESA/WorldCover/v200` | 10 m | Google Earth Engine |
| CHIRPS daily rainfall | `UCSB-CHG/CHIRPS/DAILY` | 0.05° | Google Earth Engine |
| geoBoundaries ADM3 | geoBoundaries API (government-sourced) | vector | https://www.geoboundaries.org |
| Flood-location inventory | Getachew (2025), *Addis Fortune*, Aug 3, 2025, Vol. 26, No. 1318 | n = 10 | Journalistic source, geocoded via Nominatim |

## Reproducibility note

Because the flood-location coordinates are geocoded from journalistic text
(street names, landmarks), and Nominatim's underlying OSM data can change
over time, exact re-geocoding may drift slightly from the coordinates used
in the manuscript. Consider caching the geocoded lat/lon pairs (e.g. to a
`data/geocoded_locations.csv`) the first time you run
`src/07_flood_location_inventory.py`, so later pipeline runs are reproducible
even if Nominatim's results change.
