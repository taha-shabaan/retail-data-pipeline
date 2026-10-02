"""Load walmart.grocery_sales from the datalab CSV export into PostgreSQL."""

from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path

import pandas as pd
import psycopg
from psycopg import sql

from pipeline.settings import PipelineSettings, load_settings

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CSV_NAME = "datalab_export_2026-09-29 17_47_06.csv"
SCHEMA_SQL = ROOT / "docker" / "init" / "01_schemas.sql"

GROCERY_COLUMNS = ["index", "Store_ID", "Date", "Dept", "Weekly_Sales"]


def _connect(settings: PipelineSettings) -> psycopg.Connection:
    """Open a psycopg connection using pipeline Postgres settings."""
    pg = settings.postgres
    conninfo = (
        f"host={pg.host} port={pg.port} dbname={pg.database} "
        f"user={pg.user} password={pg.password}"
    )
    return psycopg.connect(conninfo)


def wait_for_postgres(settings: PipelineSettings, timeout_seconds: int = 60) -> None:
    """Block until PostgreSQL accepts connections or raise on timeout."""
    deadline = time.monotonic() + timeout_seconds
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        try:
            with _connect(settings) as conn:
                conn.execute("SELECT 1")
            logger.info("PostgreSQL is ready")
            return
        except Exception as exc:  # noqa: BLE001 — retry until timeout
            last_error = exc
            time.sleep(1)
    raise SystemExit(f"PostgreSQL not ready after {timeout_seconds}s: {last_error}")


def apply_schema(settings: PipelineSettings) -> None:
    """Apply walmart schema DDL from docker init SQL."""
    ddl = SCHEMA_SQL.read_text(encoding="utf-8")
    with _connect(settings) as conn:
        conn.execute(ddl)
        conn.commit()
    logger.info("Applied schema from %s", SCHEMA_SQL)


def prepare_grocery_sales(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize datalab export rows for insert into walmart.grocery_sales."""
    work = df.copy()
    if "level_0" in work.columns:
        work = work.drop(columns=["level_0"])

    work["Weekly_Sales"] = work["Weekly_Sales"].astype(str).str.strip()
    work["Date"] = work["Date"].astype(str).str.strip()
    work = work[
        work["Weekly_Sales"].ne("")
        & work["Date"].ne("")
        & work["Weekly_Sales"].notna()
        & work["Date"].notna()
    ]

    work["Weekly_Sales"] = pd.to_numeric(work["Weekly_Sales"], errors="coerce")
    work["Date"] = pd.to_datetime(work["Date"], utc=True, errors="coerce").dt.date
    work = work.dropna(subset=["Weekly_Sales", "Date"])
    work = work[work["Weekly_Sales"] >= 0]

    for col in ("index", "Store_ID", "Dept"):
        work[col] = work[col].astype(int)

    return work[GROCERY_COLUMNS].sort_values(["Date", "Store_ID", "Dept"]).reset_index(drop=True)


def load_csv(csv_path: Path) -> pd.DataFrame:
    """Read the datalab grocery sales CSV from disk."""
    if not csv_path.is_file():
        raise FileNotFoundError(f"Seed CSV not found: {csv_path}")
    return pd.read_csv(csv_path)


def seed_grocery_sales(settings: PipelineSettings, prepared: pd.DataFrame) -> int:
    """Replace walmart.grocery_sales contents with prepared rows."""
    pg = settings.postgres
    table = sql.Identifier(pg.schema, pg.table)
    copy_cols = sql.SQL(", ").join(sql.Identifier(c) for c in GROCERY_COLUMNS)

    with _connect(settings) as conn:
        with conn.transaction():
            with conn.cursor() as cur:
                cur.execute(sql.SQL("TRUNCATE TABLE {}").format(table))
                with cur.copy(
                    sql.SQL("COPY {} ({}) FROM STDIN").format(table, copy_cols)
                ) as copy:
                    for row in prepared.itertuples(index=False, name=None):
                        copy.write_row(row)
    return len(prepared)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments for the seed script."""
    parser = argparse.ArgumentParser(description="Seed walmart.grocery_sales from CSV.")
    parser.add_argument(
        "--csv",
        type=Path,
        default=None,
        help=f"Path to datalab export (default: data/raw/{DEFAULT_CSV_NAME})",
    )
    parser.add_argument(
        "--wait-seconds",
        type=int,
        default=60,
        help="Max seconds to wait for Postgres (default: 60)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    """Load CSV, ensure schema, and seed grocery_sales."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = parse_args(argv)
    settings = load_settings()
    csv_path = args.csv or (settings.raw_dir / DEFAULT_CSV_NAME)

    wait_for_postgres(settings, timeout_seconds=args.wait_seconds)
    apply_schema(settings)

    raw_df = load_csv(csv_path)
    prepared = prepare_grocery_sales(raw_df)
    row_count = seed_grocery_sales(settings, prepared)
    qualified = f"{settings.postgres.schema}.{settings.postgres.table}"
    print(f"Seeded {qualified}: {row_count} rows from {csv_path}")


if __name__ == "__main__":
    main(sys.argv[1:])
