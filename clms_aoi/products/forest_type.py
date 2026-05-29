"""Forest Type product."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from clms_aoi.aoi import BoundingBox
from clms_aoi.products.base import BaseProduct

COLLECTION_ID = "4d1aad1a-f800-43c5-87d0-5565a9a31c12"

EVALSCRIPT = """
//VERSION=3
const factor = 1;
const offset = 0;
function setup() {
    return {
        input: ["FTY", "dataMask"],
        output: [
            { id: "default", bands: 4, sampleType: "UINT8" },
            { id: "index", bands: 1, sampleType: "FLOAT32" },
            { id: "browserStats", bands: 1, sampleType: "FLOAT32" },
            { id: "dataMask", bands: 1 },
        ],
    };
}

function evaluatePixel(samples) {
    const originalValue = samples.FTY;
    const val = originalValue * factor + offset;
    const dataMask = samples.dataMask;

    const EXCLUDED_VALUES = [0, 255];
    const isExcluded = dataMask === 0 || EXCLUDED_VALUES.includes(val);

    if (isExcluded) {
        return {
            default: [0, 0, 0, 0],
            index: [NaN],
            browserStats: [val],
            dataMask: [dataMask],
        };
    }

    const imgVals = getColor(originalValue);
    return {
        default: imgVals.concat(dataMask * 255),
        index: [val],
        browserStats: [val],
        dataMask: [dataMask],
    };
}

const ColorBar = [
    [1, [70, 158, 74]], // broadleaved forest
    [2, [28, 92, 36]], // coniferous forest
];
function getColor(value) {
    const closestEntry = ColorBar.reduce((prev, curr) => {
        return Math.abs(curr[0] - value) < Math.abs(prev[0] - value)
            ? curr
            : prev;
    });

    const [_, color] = closestEntry;
    return [color[0], color[1], color[2]];
}
"""


class ForestTypeProduct(BaseProduct):
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
