"""CLMS AOI — Copernicus Land Monitoring Service area-of-interest analysis tool."""

__version__ = "0.1.0"

from clms_aoi.analysis import LandCover, TreeCoverDensity, ForestType

__all__ = ["LandCover", "TreeCoverDensity", "ForestType", "__version__"]
