"""Tests for clms_aoi.outputs."""

import pandas as pd
import pytest

from clms_aoi.outputs import write_csv, write_chart


@pytest.fixture
def sample_df():
    return pd.DataFrame({"class": ["Forest", "Urban", "Water"], "area_ha": [100, 50, 25]})


def test_write_csv(tmp_path, sample_df):
    out = write_csv(sample_df, tmp_path / "out.csv")
    assert out.exists()
    loaded = pd.read_csv(out)
    assert list(loaded.columns) == ["class", "area_ha"]
    assert len(loaded) == 3


def test_write_chart(tmp_path, sample_df):
    out = write_chart(sample_df, x="class", y="area_ha", path=tmp_path / "chart.jpg")
    assert out.exists()
    assert out.stat().st_size > 0
