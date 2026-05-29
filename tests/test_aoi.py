"""Tests for clms_aoi.aoi."""

import pytest
from shapely.geometry import box
import geopandas as gpd

from clms_aoi.aoi import compute_bbox, reproject, validate_geometry, BoundingBox


def _make_gdf(minx=-1.0, miny=50.0, maxx=1.0, maxy=52.0, crs="EPSG:4326"):
    geom = box(minx, miny, maxx, maxy)
    return gpd.GeoDataFrame(geometry=[geom], crs=crs)


def test_compute_bbox():
    gdf = _make_gdf()
    bb = compute_bbox(gdf)
    assert isinstance(bb, BoundingBox)
    assert bb.west == pytest.approx(-1.0)
    assert bb.north == pytest.approx(52.0)


def test_validate_geometry_passes():
    gdf = _make_gdf()
    assert validate_geometry(gdf) is not None


def test_validate_geometry_raises_on_null():
    gdf = _make_gdf()
    gdf.loc[0, "geometry"] = None
    with pytest.raises(ValueError, match="null"):
        validate_geometry(gdf)


def test_reproject_noop_when_already_4326():
    gdf = _make_gdf(crs="EPSG:4326")
    reprojected = reproject(gdf)
    assert reprojected.crs.to_epsg() == 4326


def test_reproject_from_3857():
    from pyproj import Transformer
    t = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
    minx, miny = t.transform(-1.0, 50.0)
    maxx, maxy = t.transform(1.0, 52.0)
    gdf = _make_gdf(minx=minx, miny=miny, maxx=maxx, maxy=maxy, crs="EPSG:3857")
    reprojected = reproject(gdf)
    assert reprojected.crs.to_epsg() == 4326
