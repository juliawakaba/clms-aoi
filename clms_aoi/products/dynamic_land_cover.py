"""CORINE / Dynamic Land Cover product."""

from __future__ import annotations

from typing import Any

import pandas as pd

from clms_aoi.aoi import BoundingBox
from clms_aoi.products.base import BaseProduct

COLLECTION_ID = "828f6b20-8ffd-48f8-a1da-fefd271456db"


_STATS_EVALSCRIPT = """
//VERSION=3
function setup() {
    return {
        input: [{ bands: ["LCM10", "dataMask"] }],
        output: [
            { id: "LCM10", bands: 1, sampleType: "UINT8" },
            { id: "dataMask", bands: 1 }
        ]
    };
}
function evaluatePixel(samples) {
    return {
        LCM10: [samples.LCM10],
        dataMask: [samples.dataMask]
    };
}
"""


class DynamicLandCover(BaseProduct):
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
            return pd.DataFrame(columns=["class", "pixels", "pct"])

        bins = (
            data_items[0]["outputs"]["LCM10"]["bands"]["B0"]["histogram"]["bins"]
        )
        total = sum(b["count"] for b in bins)
        if total == 0:
            return pd.DataFrame(columns=["class", "pixels", "pct"])

        rows = []
        for b in bins:
            count = b["count"]
            if count == 0:
                continue
            midpoint = (b["lowEdge"] + b["highEdge"]) / 2
            class_value = round(midpoint / 10) * 10
            label = _CLASS_LABELS.get(class_value, f"Class {class_value}")
            rows.append({
                "class": label,
                "pixels": count,
                "pct": round(100 * count / total, 2),
            })

        return pd.DataFrame(rows).reset_index(drop=True)
