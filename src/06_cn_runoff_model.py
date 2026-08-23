"""
Manuscript Sec 3.6-3.7: Curve Number (CN) surface, SCS-CN runoff model,
and the CHIRPS rainfall-percentile scenario.

CN reflects assumed soil infiltration capacity, land cover, and antecedent
moisture under the SCS-CN framework -- it is NOT a direct measurement of
impervious surface percentage (Sec 3.6).
"""

import ee
import numpy as np

# ESA WorldCover v200 class -> CN lookup (average antecedent moisture),
# matching manuscript Sec 3.6 exactly for the five classes it specifies.
WORLDCOVER_CN_LOOKUP = {
    10: 70,   # Tree cover
    20: 65,   # Shrubland
    30: 69,   # Grassland
    40: 78,   # Cropland
    50: 88,   # Built-up
    60: 91,   # Bare / sparse vegetation
    70: 98,   # Snow and ice
    80: 100,  # Permanent water bodies
    90: 78,   # Herbaceous wetland
    95: 78,   # Mangroves
    100: 71,  # Moss and lichen
}

PERTURB_CLASSES = [10, 30, 40, 50, 60]  # classes perturbed in the +-5 sensitivity test


def build_cn_image(worldcover, lookup=None, mask_water=True):
    lookup = lookup or WORLDCOVER_CN_LOOKUP
    classes = list(lookup.keys())
    values = list(lookup.values())
    cn_image = worldcover.select("Map").remap(classes, values).rename("CN")
    if mask_water:
        water_mask = worldcover.select("Map").neq(80)
        cn_image = cn_image.updateMask(water_mask)
    return cn_image


def build_runoff_image(cn_image, p_value):
    """SCS-CN runoff depth (Eq. 1), applied per-pixel to an Earth Engine image."""
    s_image = ee.Image(25400).divide(cn_image).subtract(254)
    p_image = ee.Image(float(p_value))
    numerator = p_image.subtract(s_image.multiply(0.2)).max(0).pow(2)
    denominator = p_image.add(s_image.multiply(0.8))
    return numerator.divide(denominator).rename("runoff_mm")


def rainy_season_rainfall_percentiles(aoi):
    """
    CHIRPS daily rainfall (1981-present), restricted to the June-September
    rainy season (Sec 3.7). Returns p90, p95, p99, and the observed max.

    NOTE: we deliberately do not call this a "design storm" -- no IDF curve
    exists for this study, so a daily-rainfall percentile has no established
    equivalence to a specific annual exceedance probability (Sec 3.7).
    """
    chirps = ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY").filterBounds(aoi)
    rainy_season = chirps.filter(ee.Filter.calendarRange(6, 9, "month"))

    def daily_mean(img):
        mean_val = img.reduceRegion(
            reducer=ee.Reducer.mean(), geometry=aoi, scale=5566, maxPixels=1e9
        ).get("precipitation")
        return img.set("mean_precip", mean_val)

    rainy_season_means = rainy_season.map(daily_mean)
    precip_list = rainy_season_means.aggregate_array("mean_precip").getInfo()
    precip_arr = np.array([p for p in precip_list if p is not None])

    p90, p95, p99 = np.percentile(precip_arr, [90, 95, 99])
    pmax = precip_arr.max()
    print(f"Rainy-season daily rainfall (n={len(precip_arr)} days): "
          f"P90={p90:.1f}mm, P95={p95:.1f}mm, P99={p99:.1f}mm, max={pmax:.1f}mm")
    return {"p90": p90, "p95": p95, "p99": p99, "max": pmax, "n_days": len(precip_arr)}
