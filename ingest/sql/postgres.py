from __future__ import annotations

import logging
from pathlib import Path

import polars as pl
import psycopg

from pipeline.settings import PipelineSettings

logger = logging.getLogger(__name__)

QUERIES_DIR = Path(__file__).resolve().parent / "queries"


def _load_query(name: str) -> str:
    path = QUERIES_DIR / f"{name}.sql"
    return path.read_text(encoding="utf-8")


def _connect(settings: PipelineSettings) -> psycopg.Connection:
    pg = settings.postgres
    conninfo = (
        f"host={pg.host} port={pg.port} dbname={pg.database} "
        f"user={pg.user} password={pg.password}"
    )
    return psycopg.connect(conninfo)


def extract_table(settings: PipelineSettings, entity: str) -> pl.DataFrame:
    query = _load_query(entity)
    logger.info("Extracting %s from PostgreSQL", entity)
    with _connect(settings) as conn, conn.cursor() as cur:
        cur.execute(query)
        columns = [desc[0] for desc in cur.description]
        rows = cur.fetchall()
    return pl.DataFrame({col: [row[i] for row in rows] for i, col in enumerate(columns)})


def extract_all_sql(settings: PipelineSettings) -> dict[str, pl.DataFrame]:
    entities = ("stores", "products", "transaction_lines")
    return {name: extract_table(settings, name) for name in entities}


def write_bronze_sql(settings: PipelineSettings, frames: dict[str, pl.DataFrame]) -> None:
    out_dir = settings.bronze_dir / f"batch_id={settings.batch_id}" / "sql"
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, df in frames.items():
        path = out_dir / f"{name}.parquet"
        df.write_parquet(path)
        logger.info("Wrote bronze %s (%s rows)", path, df.height)
