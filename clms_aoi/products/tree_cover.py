"""Tree Cover Density product."""

from __future__ import annotations

from typing import Any

import pandas as pd

from clms_aoi.aoi import BoundingBox
from clms_aoi.products.base import BaseProduct

COLLECTION_ID = "3751d55a-7370-4071-9543-493ec3341d16"

# 101 bins of width 1 covering integer TCD values 0–100.
_CALCULATIONS: dict = {
    "default": {
        "histograms": {
            "TCD": {"nBins": 101, "lowEdge": -0.5, "highEdge": 100.5}
        }
    }
}

_STATS_EVALSCRIPT = """
//VERSION=3
function setup() {
    return {
        input: [{ bands: ["TCD", "dataMask"] }],
        output: [
            { id: "TCD", bands: 1, sampleType: "UINT8" },
            { id: "dataMask", bands: 1 }
        ]
    };
}
function evaluatePixel(samples) {
    return {
        TCD: [samples.TCD],
        dataMask: [samples.dataMask]
    };
}
"""

# (inclusive_low, inclusive_high, label)
_DENSITY_CLASSES: list[tuple[int, int, str]] = [
    (0, 0, "No cover (0%)"),
    (1, 10, "Very sparse (1–10%)"),
    (11, 30, "Sparse (11–30%)"),
    (31, 70, "Medium (31–70%)"),
    (71, 100, "Dense (71–100%)"),
]


class TreeCoverProduct(BaseProduct):
    COLLECTION_ID = COLLECTION_ID

    def fetch(self, bbox: BoundingBox, geometry: dict, year: int) -> Any:
        return self._fetch_statistics(
            bbox,
            geometry,
            year,
            evalscript=_STATS_EVALSCRIPT,
            calculations=_CALCULATIONS,
        )

    def summarise(self, raw: Any) -> pd.DataFrame:
        data_items = raw.get("data", [])
        if not data_items or data_items[0].get("status") != "OK":
            return pd.DataFrame(columns=["density_class", "pixels", "pct"])

        bins = (
            data_items[0]["outputs"]["TCD"]["bands"]["B0"]["histogram"]["bins"]
        )

        # Map each integer TCD value (0–100) to its pixel count.
        value_counts: dict[int, int] = {}
        for b in bins:
            value = round((b["lowEdge"] + b["highEdge"]) / 2)
            value_counts[value] = b["count"]

        total = sum(value_counts.values())
        if total == 0:
            return pd.DataFrame(columns=["density_class", "pixels", "pct"])

        rows = []
        for lo, hi, label in _DENSITY_CLASSES:
            count = sum(value_counts.get(v, 0) for v in range(lo, hi + 1))
            if count == 0:
                continue
            rows.append({
                "density_class": label,
                "pixels": count,
                "pct": round(100 * count / total, 2),
            })

        return pd.DataFrame(rows).reset_index(drop=True)
