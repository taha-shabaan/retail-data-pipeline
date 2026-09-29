from __future__ import annotations

import logging
from pathlib import Path

import polars as pl

from pipeline.settings import PipelineSettings

logger = logging.getLogger(__name__)

EXPECTED_PRODUCT_SUPPLEMENT = {
    "product_id": pl.Int64,
    "category_override": pl.Utf8,
    "is_promotional": pl.Boolean,
}


def read_product_supplement(settings: PipelineSettings) -> pl.DataFrame:
    path = settings.raw_dir / settings.product_supplement_filename
    if not path.exists():
        raise FileNotFoundError(
            f"Missing Parquet source at {path}. Run: make seed"
        )
    logger.info("Reading Parquet supplement %s", path)
    df = pl.read_parquet(path)
    _validate_schema(df, EXPECTED_PRODUCT_SUPPLEMENT, "product_supplement")
    return df


def write_bronze_parquet(settings: PipelineSettings, df: pl.DataFrame) -> Path:
    out_dir = settings.bronze_dir / f"batch_id={settings.batch_id}" / "parquet"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / settings.product_supplement_filename
    df.write_parquet(path)
    logger.info("Wrote bronze %s (%s rows)", path, df.height)
    return path


def _validate_schema(df: pl.DataFrame, expected: dict[str, pl.DataType], label: str) -> None:
    missing = set(expected) - set(df.columns)
    if missing:
        raise ValueError(f"{label}: missing columns {sorted(missing)}")
    for col, dtype in expected.items():
        if df.schema[col] != dtype:
            raise ValueError(f"{label}: column {col} expected {dtype}, got {df.schema[col]}")
