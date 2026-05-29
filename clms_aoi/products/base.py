"""Shared interface that every product module implements."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import requests
import pandas as pd

from clms_aoi.aoi import BoundingBox
from clms_aoi.auth import TokenCache

_STATS_URL = "https://services.sentinel-hub.com/api/v1/statistics"


class BaseProduct(ABC):
    """Abstract base for a CLMS product fetcher + summariser."""

    #: Sentinel Hub collection ID (BYOC).
    COLLECTION_ID: str = ""

    def __init__(self, token_cache: TokenCache) -> None:
        self._token_cache = token_cache

    @abstractmethod
    def fetch(self, bbox: BoundingBox, geometry: dict, year: int) -> Any:
        """Fetch raw statistics for *bbox*/*geometry* in *year*."""

    @abstractmethod
    def summarise(self, raw: Any) -> pd.DataFrame:
        """Convert the raw fetch result into a summary DataFrame."""

    def run(self, bbox: BoundingBox, geometry: dict, year: int) -> pd.DataFrame:
        """Convenience: fetch then summarise."""
        return self.summarise(self.fetch(bbox, geometry, year))

    def _fetch_statistics(
        self,
        bbox: BoundingBox,
        geometry: dict,
        year: int,
        evalscript: str,
        calculations: dict,
        resolution: float = 0.001,
    ) -> dict:
        """Call the Sentinel Hub Statistical API and return the parsed JSON."""
        token = self._token_cache.get_token()
        body = {
            "input": {
                "bounds": {
                    "geometry": geometry,
                    "properties": {
                        "crs": "http://www.opengis.net/def/crs/EPSG/0/4326"
                    },
                },
                "data": [
                    {
                        "type": f"byoc-{self.COLLECTION_ID}",
                        "dataFilter": {
                            "timeRange": {
                                "from": f"{year}-01-01T00:00:00Z",
                                "to": f"{year}-12-31T23:59:59Z",
                            }
                        },
                    }
                ],
            },
            "aggregation": {
                "timeRange": {
                    "from": f"{year}-01-01T00:00:00Z",
                    "to": f"{year}-12-31T23:59:59Z",
                },
                "aggregationInterval": {"of": "P1Y"},
                "evalscript": evalscript,
                "resx": resolution,
                "resy": resolution,
            },
            "calculations": calculations,
        }
        resp = requests.post(
            _STATS_URL,
            json=body,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            timeout=120,
        )
        resp.raise_for_status()
        return resp.json()
