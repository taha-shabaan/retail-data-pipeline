# Implementation plan (locked decisions)

This document captures the design choices for the retail pipeline project and how they map to the repo and LinkedIn series.

## Goals


| Decision         | Choice                                                                     |
| ---------------- | -------------------------------------------------------------------------- |
| Deliverable      | Repo structure **and** LinkedIn posts (one section ↔ one post)             |
| Primary audience | Hiring managers and tech recruiters (90-second GitHub skim)                |
| Maturity         | Runnable MVP + senior signals (tests, CI, Makefile, runbook, config)       |
| Stack            | PostgreSQL (Docker), Parquet files, Python + Polars, DuckDB + Parquet gold |
| Modeling         | Star core (`fct_sales`, dims) + **wide gold marts** for consumption        |
| Publishing       | **6 posts**; post #1 = README + architecture landing page                  |
| Voice            | First person (“I built…”), **Walmart-inspired** retail, not affiliated     |




## Entity scope (MVP)

- Stores, products, transaction lines (line-item grain for `fct_sales`)
- Parquet supplement for category/promo attributes (second source type)
- Calendar / promotions reserved for phase 2



## Repo map


| Path              | Responsibility                                     |
| ----------------- | -------------------------------------------------- |
| `docker/`         | PostgreSQL operational source                      |
| `ingest/sql/`     | Extract from RDBMS via versioned SQL               |
| `ingest/parquet/` | Extract file feeds with schema validation          |
| `transform/`      | Clean, enrich, quality rules                       |
| `model/marts/`    | Build wide marts from silver star pieces           |
| `load/`           | DuckDB + partitioned Parquet                       |
| `pipeline/`       | Single batch entrypoint                            |
| `tests/`          | Transform, model, ingest unit/integration          |
| `docs/`           | Architecture, dictionary, runbook, LinkedIn drafts |




## LinkedIn sequence

1. Architecture + repo map — `README.md`, `docs/architecture.md`
2. SQL extract — `docker/`, `ingest/sql/`
3. Parquet extract — `ingest/parquet/`, `data/raw/`
4. Transform + tests — `transform/`, `tests/`
5. Star → wide marts — `model/`, `load/`
6. Production next steps — `docs/runbook.md`, `.github/workflows/`



## Phase 2 (not in MVP)

- Incremental extract (watermarks)
- Postgres load for BI demo schema
- Orchestrator (Dagster/Airflow) wrapping `pipeline/run_batch.py`
- Great Expectations or SOperational (PostgreSQL)oda on silver contracts

