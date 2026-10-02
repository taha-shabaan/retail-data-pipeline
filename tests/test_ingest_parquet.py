from pathlib import Path

import pandas as pd
import pytest

from ingest.parquet.reader import read_extra_data
from pipeline.settings import PipelineSettings, PostgresSettings


@pytest.fixture
def settings(tmp_path: Path) -> PipelineSettings:
    raw = tmp_path / "raw"
    raw.mkdir()
    pd.DataFrame(
        {
            "Store_ID": [1],
            "Date": pd.to_datetime(["2010-02-05"]),
            "IsHoliday": [0],
            "Temperature": [40.0],
            "Fuel_Price": [2.5],
            "CPI": [210.0],
            "Unemployment": [8.0],
            "MarkDown1": [0.0],
            "MarkDown2": [0.0],
            "MarkDown3": [0.0],
            "MarkDown4": [0.0],
            "Dept": [1],
            "Size": [100],
            "Type": ["A"],
        }
    ).to_parquet(raw / "extra_data.parquet", index=False)
    return PipelineSettings(
        batch_id="test",
        data_root=tmp_path,
        raw_dir=raw,
        bronze_dir=tmp_path / "bronze",
        processed_dir=tmp_path / "processed",
        postgres=PostgresSettings(
            "localhost", 15432, "retail", "retail", "retail", "walmart", "grocery_sales"
        ),
        extra_data_filename="extra_data.parquet",
        clean_data_csv_name="clean_data.csv",
        agg_data_csv_name="agg_data.csv",
    )


def test_read_extra_data(settings: PipelineSettings):
    df = read_extra_data(settings)
    assert len(df) == 1
