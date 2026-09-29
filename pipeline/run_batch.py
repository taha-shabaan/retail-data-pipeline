from __future__ import annotations

import logging
import sys

from ingest.parquet.reader import read_product_supplement, write_bronze_parquet
from ingest.sql.postgres import extract_all_sql, write_bronze_sql
from load.duckdb_loader import load_marts, write_gold_parquet
from model.marts.build import build_gold_marts
from pipeline.logging_setup import configure_logging
from pipeline.settings import ensure_data_dirs, load_settings
from transform.quality.checks import build_silver

logger = logging.getLogger(__name__)


def run() -> int:
    configure_logging()
    settings = load_settings()
    ensure_data_dirs(settings)
    logger.info("Starting batch pipeline batch_id=%s", settings.batch_id)

    sql_frames = extract_all_sql(settings)
    write_bronze_sql(settings, sql_frames)

    supplement = read_product_supplement(settings)
    write_bronze_parquet(settings, supplement)

    silver = build_silver(
        stores=sql_frames["stores"],
        products=sql_frames["products"],
        lines=sql_frames["transaction_lines"],
        supplement=supplement,
    )

    silver_out = settings.silver_dir / f"batch_id={settings.batch_id}"
    silver_out.mkdir(parents=True, exist_ok=True)
    for name, df in silver.items():
        df.write_parquet(silver_out / f"{name}.parquet")

    marts = build_gold_marts(silver)
    write_gold_parquet(settings.gold_dir, settings.batch_id, marts)
    load_marts(settings.duckdb_path, marts)

    logger.info("Pipeline finished successfully")
    return 0


if __name__ == "__main__":
    sys.exit(run())
