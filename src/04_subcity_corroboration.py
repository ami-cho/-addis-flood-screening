"""
Manuscript Sec 4.3: sub-city spatial corroboration.

Classifies the top-50 flow-accumulation road points against Addis Ababa's
ten sub-city (woreda-level ADM3) boundaries, pulled from geoBoundaries
(government-sourced), and compares descriptively against the sub-cities
independently identified as most flood-susceptible by Bekalo et al. (2025).

This is corroboration between two independently built models -- not
validation against flood occurrence (that's script 08).
"""

import geopandas as gpd
import requests
from shapely.geometry import Point

GEOBOUNDARIES_URL = "https://www.geoboundaries.org/api/current/gbOpen/ETH/ADM3/"

# Addis Ababa's ten sub-cities as they appear (with spelling variants) in the
# geoBoundaries ADM3 shapeName field.
ADDIS_SUBCITY_NAMES = [
    "Nefas Silk", "Bole", "Lideta", "Kirkos", "Yeka",
    "Addis Ketema", "Arada", "Gulele", "Akaki - Kalit", "Kolfe - Keran",
]


def load_subcity_boundaries():
    resp = requests.get(GEOBOUNDARIES_URL)
    meta = resp.json()
    geojson_url = meta["gjDownloadURL"]
    eth_admin3 = gpd.read_file(geojson_url)

    addis_gdf = eth_admin3[eth_admin3["shapeName"].isin(ADDIS_SUBCITY_NAMES)]
    print(f"Found {len(addis_gdf)} of 10 expected sub-cities")
    if len(addis_gdf) < 10:
        print(
            "Fewer than 10 matched -- check shapeName spelling variants "
            "(e.g. 'Akaki'/'Akaky', 'Kaliti'/'Kality')."
        )
    return addis_gdf


def classify_subcity(top_points_gdf, addis_gdf):
    def find_subcity(row):
        pt = Point(row["lon"], row["lat"])
        for _, boundary_row in addis_gdf.iterrows():
            if boundary_row.geometry.contains(pt):
                return boundary_row["shapeName"]
        return "Unmatched"

    top_points_gdf = top_points_gdf.copy()
    top_points_gdf["subcity"] = top_points_gdf.apply(find_subcity, axis=1)
    return top_points_gdf
