"""Tree Cover Density product."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from clms_aoi.aoi import BoundingBox
from clms_aoi.products.base import BaseProduct

COLLECTION_ID = "3751d55a-7370-4071-9543-493ec3341d16"

EVALSCRIPT = """
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


class TreeCoverProduct(BaseProduct):
    COLLECTION_ID = COLLECTION_ID

    def visualize(self, bbox: BoundingBox, geometry: dict, year: int) -> Any:
        lulc_img = self._request_data(
            bbox,
            geometry,
            year,
            evalscript=EVALSCRIPT,
        )
        print(
            f"Returned data is of type = {type(lulc_img)} and length {len(lulc_img)}.")
        return lulc_img

    def statistics(self, bbox: BoundingBox, geometry: dict, year: int) -> Any:
        # stats = self._request_data(
        #     bbox,
        #     geometry,
        #     year,
        #     evalscript=_STATS_EVALSCRIPT,
        # )
        result = np.random.rand(10, 10)  # Placeholder for actual stats
        print(
            f"Returned data is of type = {"stats"} and length {len(result)}.")
        return result
