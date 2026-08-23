"""
Manuscript Sec 3.8: independent flood-location inventory.

Ten specific, dated flood locations drawn from an August 2025 investigative
report (Getachew, 2025), independent of any academic source or this study's
models. Geocoded via OSM/Nominatim using the most specific landmark
available in the source text.

NOTE: the archived original notebook geocoded these locations twice --
an initial pass with looser neighborhood-level queries, then a corrected
pass (this one) using more specific landmarks (e.g. "St. Estifanos Church"
rather than "OLA gas station"). This file reflects the final, corrected
version actually used for Table 6 in the manuscript.
"""

import osmnx as ox

NAMED_FLOOD_LOCATIONS = {
    "OLA station / St. Estifanos Church, Menelik II Ave": "St. Estifanos Church, Addis Ababa, Ethiopia",
    "Ghion Hotel, Menelik II Ave": "Ghion Hotel, Addis Ababa, Ethiopia",
    "Ring Road, Bole area": "Bole, Addis Ababa, Ethiopia",
    "Kotebe": "Kotebe, Addis Ababa, Ethiopia",
    "Betel": "Betel, Addis Ababa, Ethiopia",
    "Summit Road": "Summit, Addis Ababa, Ethiopia",
    "Mexico Square-Saris corridor (Bulgaria area)": "Bulgaria, Addis Ababa, Ethiopia",
    "Gurd Shola Bridge": "Gurd Shola, Addis Ababa, Ethiopia",
    "Mekanisa": "Mekanisa, Addis Ababa, Ethiopia",
    "CMC Square": "CMC, Addis Ababa, Ethiopia",
}


def geocode_flood_locations(locations=None):
    locations = locations or NAMED_FLOOD_LOCATIONS
    geocoded = {}
    for label, query in locations.items():
        try:
            pt = ox.geocode(query)  # returns (lat, lon)
            geocoded[label] = pt
            print(f"{label}: {pt}")
        except Exception as e:
            print(f"Failed to geocode '{label}' ({query}): {e}")
    if len(geocoded) < len(locations):
        print(
            f"WARNING: only geocoded {len(geocoded)}/{len(locations)} locations. "
            "Manuscript Sec 3.8/6 flags that positional uncertainty from "
            "text-based geocoding has not been formally quantified per point."
        )
    return geocoded
