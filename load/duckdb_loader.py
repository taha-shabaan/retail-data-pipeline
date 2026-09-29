from __future__ import annotations

import logging
from pathlib import Path

import duckdb
import polars as pl

logger = logging.getLogger(__name__)


def load_marts(duckdb_path: Path, marts: dict[str, pl.DataFrame]) -> None:
    duckdb_path.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(duckdb_path))
    try:
        for name, df in marts.items():
            con.register("_mart_frame", df)
            con.execute(f"CREATE OR REPLACE TABLE {name} AS SELECT * FROM _mart_frame")
            con.unregister("_mart_frame")
            logger.info("Loaded DuckDB table %s (%s rows)", name, df.height)
    finally:
        con.close()


def write_gold_parquet(gold_dir: Path, batch_id: str, marts: dict[str, pl.DataFrame]) -> None:
    base = gold_dir / f"batch_id={batch_id}"
    base.mkdir(parents=True, exist_ok=True)
    for name, df in marts.items():
        path = base / f"{name}.parquet"
        df.write_parquet(path)
        logger.info("Wrote gold %s", path)
