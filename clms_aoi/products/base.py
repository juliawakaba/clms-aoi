"""Shared interface that every product module implements."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import pandas as pd

from clms_aoi.aoi import BoundingBox


class BaseProduct(ABC):
    """Abstract base for a CLMS product fetcher + summariser."""

    #: Sentinel Hub collection ID (BYOC or a known dataset).
    COLLECTION_ID: str = ""

    #: Evalscript used in the Process API request (override if needed).
    EVALSCRIPT: str = ""

    def __init__(self, token: str) -> None:
        self._token = token

    @abstractmethod
    def fetch(self, bbox: BoundingBox, date: str) -> Any:
        """Fetch the raw raster/response for *bbox* on *date* (YYYY-MM-DD)."""

    @abstractmethod
    def summarise(self, raw: Any) -> pd.DataFrame:
        """Convert the raw fetch result into a summary DataFrame."""

    def run(self, bbox: BoundingBox, date: str) -> pd.DataFrame:
        """Convenience: fetch then summarise."""
        return self.summarise(self.fetch(bbox, date))
