"""Read, validate, reproject, and summarise an area-of-interest geometry."""

from __future__ import annotations

from pathlib import Path
from typing import NamedTuple

import geopandas as gpd
from shapely.geometry import box, mapping

# Sentinel Hub Process API expects WGS-84 for the bbox/geometry fields.
_SH_CRS = "EPSG:4326"


class BoundingBox(NamedTuple):
    west: float
    south: float
    east: float
    north: float

    def to_list(self) -> list[float]:
        return [self.west, self.south, self.east, self.north]


def load_aoi(path: str | Path) -> gpd.GeoDataFrame:
    """Read a GeoJSON or GeoPackage file and return a GeoDataFrame."""
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix in {".geojson", ".json"}:
        gdf = gpd.read_file(path, driver="GeoJSON")
    elif suffix in {".gpkg"}:
        gdf = gpd.read_file(path, driver="GPKG")
    else:
        # Let geopandas sniff the driver for any other supported format.
        gdf = gpd.read_file(path)
    return gdf


def validate_geometry(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Raise ValueError if any geometry is null or invalid."""
    if gdf.geometry.isnull().any():
        raise ValueError("AOI contains null geometries.")
    invalid = ~gdf.geometry.is_valid
    if invalid.any():
        raise ValueError(
            f"AOI contains {invalid.sum()} invalid geometry/geometries. "
            "Run gdf.geometry.buffer(0) to attempt repair."
        )
    return gdf


def reproject(gdf: gpd.GeoDataFrame, crs: str = _SH_CRS) -> gpd.GeoDataFrame:
    """Reproject to *crs* (default: EPSG:4326 required by Sentinel Hub)."""
    if gdf.crs is None:
        raise ValueError("AOI GeoDataFrame has no CRS set.")
    if gdf.crs.to_epsg() != int(crs.split(":")[1]):
        gdf = gdf.to_crs(crs)
    return gdf


def compute_bbox(gdf: gpd.GeoDataFrame) -> BoundingBox:
    """Return the axis-aligned bounding box of the entire GeoDataFrame."""
    minx, miny, maxx, maxy = gdf.total_bounds
    return BoundingBox(west=minx, south=miny, east=maxx, north=maxy)


def aoi_geojson(gdf: gpd.GeoDataFrame) -> dict:
    """Return a GeoJSON-compatible dict of the union of all AOI geometries."""
    union = gdf.geometry.union_all()
    return mapping(union)


def compute_area_ha(gdf: gpd.GeoDataFrame) -> float:
    """Compute total area of AOI in hectares using an equal-area projection."""
    gdf_ea = gdf.to_crs("EPSG:6933")
    return float(gdf_ea.geometry.area.sum() / 10_000)


def prepare_aoi(path: str | Path) -> tuple[gpd.GeoDataFrame, BoundingBox]:
    """Full pipeline: load → validate → reproject → bbox."""
    gdf = load_aoi(path)
    gdf = validate_geometry(gdf)
    gdf = reproject(gdf)
    bbox = compute_bbox(gdf)
    return gdf, bbox
