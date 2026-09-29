# Architecture

## Problem

Retail analytics depends on **operational SQL** (stores, products, transactions) and **file-based history or partner feeds** (Parquet). Data engineers unify those sources into **trusted, easy-to-query marts** without forcing analysts to understand every upstream quirk.

This project is **inspired by Walmart-style multinational retail**. It is an educational portfolio piece—not affiliated with Walmart.

## Context diagram

```
┌─────────────────────┐     ┌──────────────────────────┐
│ PostgreSQL          │     │ Parquet (raw/)           │
│ operational.*       │     │ product_supplement       │
└─────────┬───────────┘     └────────────┬─────────────┘
          │ extract                      │ extract
          └──────────────┬───────────────┘
                         ▼
                 ┌───────────────┐
                 │ bronze/       │  batch_id partition
                 └───────┬───────┘
                         ▼
                 ┌───────────────┐
                 │ transform     │  quality rules, enrich
                 └───────┬───────┘
                         ▼
                 ┌───────────────┐
                 │ silver/       │  dim_*, fct_sales
                 └───────┬───────┘
                         ▼
                 ┌───────────────┐
                 │ gold marts    │  wide tables for BI
                 └───────┬───────┘
                         ▼
          ┌──────────────┴──────────────┐
          ▼                             ▼
   Parquet (gold/)              DuckDB file
```

## Layers

| Layer | Purpose | Location |
|-------|---------|----------|
| Operational | Source of truth for live retail entities | PostgreSQL `operational` schema |
| Raw / bronze | Immutable-ish landing with batch metadata | `data/bronze/batch_id=…` |
| Silver | Cleaned entities + fact at documented grain | `data/silver/…`, `fct_sales` = **line item** |
| Gold | Wide marts for consumption | `mart_daily_store_sales`, `mart_product_performance` |

## Design choices

1. **Two extract patterns, one pipeline contract** — SQL and Parquet both land in bronze before transform.
2. **Star logic, wide delivery** — Facts and dims exist in silver; gold exposes join-light marts.
3. **Batch orchestration in code** — `pipeline/run_batch.py` is the unit you would schedule; no orchestrator in MVP.
4. **Config vs secrets** — Paths and names in `config/settings.yaml`; credentials in `.env`.

## Production extensions (documented, not built)

- Watermarked incremental SQL extract
- Dead-letter quarantine for bad Parquet rows
- OpenTelemetry metrics on row counts and duration per stage
- Airflow/Dagster DAG calling the same stages
