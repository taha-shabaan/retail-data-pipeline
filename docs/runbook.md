# Runbook

## Prerequisites

- Docker (for PostgreSQL)
- Python 3.11+

## First-time setup

```bash
cp .env.example .env
make setup
make seed    # starts Postgres + writes sample Parquet to data/raw/
make pipeline
```

## Verify output

```bash
# DuckDB CLI if installed:
duckdb data/duckdb/retail_analytics.duckdb -c "SELECT * FROM mart_daily_store_sales LIMIT 5;"

# Or Python:
.venv/bin/python -c "import duckdb; print(duckdb.connect('data/duckdb/retail_analytics.duckdb').sql('SELECT * FROM mart_daily_store_sales').df())"
```

PostgreSQL listens on host port **15432** by default (see `docker/compose.yml`) to avoid clashing with a local Postgres on 5432.

Gold Parquet files appear under `data/gold/batch_id=dev/`.

## Common failures

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Connection refused to Postgres | Container not up | `make up`, wait for healthy status |
| Missing Parquet source | Raw file not generated | `make seed` or `python scripts/generate_sample_parquet.py` |
| Schema validation error on supplement | Column drift in file | Align with `docs/data_dictionary.md` |
| Empty marts | Seed SQL not loaded | Recreate volume: `make down`, `docker volume prune` (careful), `make seed` |

## Backfill (manual)

1. Set `BATCH_ID` and optional date filters in SQL (future: watermark table).
2. Run `make pipeline`.
3. Compare row counts in bronze vs silver vs gold logs.

## CI

GitHub Actions runs `ruff` and `pytest` with a Postgres service and applies `docker/init/*.sql`.
