# Retail Data Pipeline

Batch ETL for **Walmart-inspired multinational retail**: extract from **PostgreSQL** and **Parquet**, transform with tested quality rules, model **facts and dimensions**, and publish **wide gold marts** for easy analytics (DuckDB + Parquet).

Educational portfolio project — **not affiliated with Walmart**.

## Why this exists

Retail data rarely sits in one place. Stores and transactions live in operational SQL; partner feeds and historical archives show up as files. I built this pipeline to show how I unify those sources with clear layers, contracts, and tests—the same habits I’d bring to a production batch platform.

## Architecture

See [docs/architecture.md](docs/architecture.md) for the full diagram. Short flow:

```
PostgreSQL (operational) ──┐
                           ├──► bronze → transform → silver → gold marts → DuckDB / Parquet
Parquet (raw/) ────────────┘
```

## Repo map

| Path | Role |
|------|------|
| [docker/](docker/) | PostgreSQL source database |
| [ingest/sql/](ingest/sql/) | SQL extract + versioned queries |
| [ingest/parquet/](ingest/parquet/) | Parquet extract + schema checks |
| [transform/](transform/) | Cleaning, enrich, quality rules |
| [model/marts/](model/marts/) | Wide marts from silver facts/dims |
| [load/](load/) | DuckDB and gold Parquet writer |
| [pipeline/](pipeline/) | Batch entrypoint (`run_batch.py`) |
| [tests/](tests/) | pytest (transform, model, ingest) |
| [docs/](docs/) | Dictionary, runbook, LinkedIn drafts |
| [docs/implementation-plan.md](docs/implementation-plan.md) | Locked design decisions |

## Stack

| Area | Choice |
|------|--------|
| Extract (SQL) | PostgreSQL 16, psycopg, SQL files |
| Extract (files) | Polars, Parquet |
| Transform / model | Polars |
| Load | DuckDB, Parquet partitions |
| Quality / CI | pytest, ruff, GitHub Actions |

## Quick start

```bash
cp .env.example .env
make setup
make seed      # docker up + sample Parquet in data/raw/
make pipeline
```

Query marts:

```bash
duckdb data/duckdb/retail_analytics.duckdb -c "SELECT * FROM mart_daily_store_sales;"
```

Details and troubleshooting: [docs/runbook.md](docs/runbook.md).

## Data model (gold)

| Mart | Grain |
|------|--------|
| `mart_daily_store_sales` | `sale_date` + `store_id` |
| `mart_product_performance` | `product_id` |

Column definitions: [docs/data_dictionary.md](docs/data_dictionary.md).

## LinkedIn series

Draft posts aligned to each pipeline phase: [docs/linkedin/](docs/linkedin/).

## License

MIT — see [LICENSE](LICENSE).
