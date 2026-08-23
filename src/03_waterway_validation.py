"""
Manuscript Sec 4.2: hydrological consistency check -- distance from the
top-ranked flow-accumulation points to the nearest independently mapped
OSM waterway. This validates internal hydrological plausibility (does the
terrain layer find real channels?), not flood occurrence.
"""

import geopandas as gpd
import osmnx as ox
from shapely.ops import unary_union


PLACE = "Addis Ababa, Ethiopia"


def get_waterways(grid_crs):
    waterways = ox.features_from_place(PLACE, tags={"waterway": True})
    waterways = waterways.to_crs(grid_crs)
    print(f"Waterway features found: {len(waterways)}")
    return waterways


def distance_to_waterway_m(point_geom, waterway_union, source_crs):
    """Project to UTM 37N (EPSG:32637, covers Addis Ababa) for an accurate
    metric distance."""
    point_m = gpd.GeoSeries([point_geom], crs=source_crs).to_crs(epsg=32637).iloc[0]
    water_m = gpd.GeoSeries([waterway_union], crs=source_crs).to_crs(epsg=32637).iloc[0]
    return point_m.distance(water_m)


def add_waterway_distances(top_points_gdf, grid_crs):
    """Adds a `dist_to_waterway_m` column to the top flow-accumulation points
    (Table 2 in the manuscript)."""
    waterways = get_waterways(grid_crs)
    waterway_union = unary_union(waterways.geometry)
    top_points_gdf = top_points_gdf.copy()
    top_points_gdf["dist_to_waterway_m"] = top_points_gdf["midpoint"].apply(
        lambda pt: distance_to_waterway_m(pt, waterway_union, grid_crs)
    )
    return top_points_gdf
