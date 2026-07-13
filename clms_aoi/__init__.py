"""CLMS AOI — Copernicus Land Monitoring Service area-of-interest analysis tool."""
__version__ = "0.1.0"

from .config import ConfigLoader, SentinelHubCredentials
from .auth import SentinelHubAuthenticator
from .exceptions import ClmsAoiError

# The below define what gets exported when someone runs: from clms_aoi import *
__all__ = [
    "ConfigLoader",
    "SentinelHubCredentials",
    "SentinelHubAuthenticator",
    "ClmsAoiError",
    "__version__",
]

# __version__ = "0.1.0"

# from clms_aoi.analysis import LandCover, TreeCoverDensity, ForestType

# __all__ = ["LandCover", "TreeCoverDensity", "ForestType", "__version__"]
