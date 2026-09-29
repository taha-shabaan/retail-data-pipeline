from pathlib import Path

import polars as pl
import pytest

from ingest.parquet.reader import read_product_supplement
from pipeline.settings import PipelineSettings, PostgresSettings


@pytest.fixture
def settings(tmp_path: Path) -> PipelineSettings:
    raw = tmp_path / "raw"
    raw.mkdir()
    pl.DataFrame(
        {
            "product_id": [1],
            "category_override": ["X"],
            "is_promotional": [True],
        }
    ).write_parquet(raw / "product_supplement.parquet")
    return PipelineSettings(
        batch_id="test",
        data_root=tmp_path,
        raw_dir=raw,
        bronze_dir=tmp_path / "bronze",
        silver_dir=tmp_path / "silver",
        gold_dir=tmp_path / "gold",
        duckdb_path=tmp_path / "duckdb" / "test.duckdb",
        postgres=PostgresSettings("localhost", 5432, "retail", "retail", "retail"),
        product_supplement_filename="product_supplement.parquet",
    )


def test_read_product_supplement(settings: PipelineSettings):
    df = read_product_supplement(settings)
    assert df.height == 1
