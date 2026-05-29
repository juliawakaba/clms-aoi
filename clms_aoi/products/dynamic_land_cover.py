"""CORINE Land Cover product."""

from __future__ import annotations

from typing import Any

import pandas as pd

from clms_aoi.aoi import BoundingBox
from clms_aoi.products.base import BaseProduct

COLLECTION_ID = "828f6b20-8ffd-48f8-a1da-fefd271456db"

EVALSCRIPT = """
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


class CorineProduct(BaseProduct):
    COLLECTION_ID = COLLECTION_ID
    EVALSCRIPT = EVALSCRIPT

    def fetch(self, bbox: BoundingBox, date: str) -> Any:
        raise NotImplementedError

    def summarise(self, raw: Any) -> pd.DataFrame:
        raise NotImplementedError
