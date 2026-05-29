"""CORINE / Dynamic Land Cover product."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from clms_aoi.aoi import BoundingBox
from clms_aoi.products.base import BaseProduct

COLLECTION_ID = "828f6b20-8ffd-48f8-a1da-fefd271456db"


_STATS_EVALSCRIPT = """
//VERSION=3

function setup() {
    return {
        input: ["LCM10", "dataMask"],
        output: {
            bands: 4,
            sampleType: "AUTO",
        },
    };
}

const map = [
    [10, 0x006400],
    [20, 0xffbb22],
    [30, 0xffff4c],
    [40, 0xf096ff],
    [50, 0x0096a0],
    [60, 0x00cf75],
    [70, 0xfae6a0],
    [80, 0xb4b4b4],
    [90, 0xfa0000],
    [100, 0x0064c8],
    [110, 0xf0f0f0],
    [254, 0x0a0a0a],
];

const visualizer = new ColorMapVisualizer(map);

function evaluatePixel(sample) {
    return visualizer.process(sample.LCM10).concat(sample.dataMask);
}
"""


lulc_colors = {
    10:  ([0, 100, 0],     "Tree cover"),
    20:  ([255, 187, 34],  "Shrubland"),
    30:  ([255, 255, 76],  "Grassland"),
    40:  ([240, 150, 255], "Cropland"),
    50:  ([250, 0, 0],     "Built-up"),
    60:  ([180, 180, 180], "Bare/sparse vegetation"),
    70:  ([240, 240, 240], "Snow and ice"),
    80:  ([0, 100, 200],   "Permanent water bodies"),
    90:  ([0, 150, 160],   "Herbaceous wetland"),
    95:  ([0, 207, 117],   "Mangroves"),
    100: ([250, 230, 160], "Moss and lichen"),
    254: ([10, 10, 10],    "Unclassifiable"),
}


class DynamicLandCover(BaseProduct):
    COLLECTION_ID = COLLECTION_ID

    def visualize(self, bbox: BoundingBox, geometry: dict, year: int) -> Any:
        lulc_img = self._request_data(
            bbox,
            geometry,
            year,
            evalscript=_STATS_EVALSCRIPT,
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
