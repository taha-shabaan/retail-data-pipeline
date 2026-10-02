# Business requirements — Walmart holiday sales analysis

## Context

Walmart is the largest retailer in the United States and continues to grow its **e-commerce** channel. By the end of **2022**, online sales reached roughly **$80 billion**, about **13%** of total company sales. Planning inventory, staffing, and promotions requires understanding **supply and demand**, especially around **public holidays** (Super Bowl, Labor Day, Thanksgiving, Christmas, and similar events) when customer traffic and basket sizes shift quickly.

## Problem statement

Analytics and merchandising teams need a **trusted, repeatable dataset** that combines:

1. **Weekly store sales** from the operational database (`grocery_sales` in PostgreSQL).
2. **Complementary context** from a partner file (`extra_data.parquet`): holidays, macro indicators (CPI, unemployment), fuel prices, markdowns, and store/department attributes.

Without a pipeline, analysts merge spreadsheets manually, miss schema changes, and produce inconsistent monthly views of performance.

## Objectives

| ID | Objective | Success measure |
|----|-----------|-----------------|
| O1 | Ingest both sources on a schedule (batch MVP: on demand) | Zero manual copy-paste for routine refreshes |
| O2 | Produce **`clean_data`** with a documented column set | Downstream notebooks/BI use one grain |
| O3 | Run **preliminary analysis** — monthly view of sales | **`agg_data`** published with pipeline |
| O4 | Persist outputs for stakeholders | `clean_data.csv` and `agg_data.csv` in `data/processed/` |
| O5 | Support holiday-focused analysis | `IsHoliday` and calendar month available in `clean_data` |

## Stakeholders

| Stakeholder | Need |
|-------------|------|
| Merchandising / supply chain | Month and department-level sales vs holidays |
| Store operations | Store type/size context from Parquet |
| Data & analytics | Stable schemas, reproducible transforms |
| Leadership | Directional monthly sales trend (`agg_data`) |

## Scope (in)

- Extract `walmart.grocery_sales` from PostgreSQL (Docker).
- Extract `extra_data.parquet` from `data/raw/` (mounted in Docker at `/data/raw` for visibility).
- Merge on **`Store_ID`** and **`Date`** (weekly sales week).
- Derive **`Month`** from `Date`.
- Output columns for **`clean_data`**: `Store_ID`, `Month`, `Dept`, `IsHoliday`, `Weekly_Sales`, `CPI`, `Unemployment`.
- Aggregate to **`agg_data`**: `Month`, `Weekly_Sales` (mean weekly sales across rows in that month for this MVP).
- Export both frames to CSV.

## Scope (out) — phase 2

- Real-time streaming or intraday e-commerce events.
- Production orchestration (Airflow/Dagster), data contracts service, and ML forecasting.
- Official Walmart datasets or proprietary feeds (this repo uses **sample** data for learning).

## Non-functional requirements

| Area | Requirement |
|------|-------------|
| Reproducibility | `make seed && make pipeline` on a clean clone |
| Tooling | **pandas** for transform and analysis (project standard) |
| Secrets | Postgres password via `.env`, not committed |
| Documentation | Architecture, data dictionary, and pipeline steps kept in sync with code |

## Key business questions (analysis)

1. How do **average weekly sales** change by **calendar month**?
2. Which **months** show higher sales when **`IsHoliday`** weeks are included?
3. How do **CPI** and **Unemployment** align with monthly sales movement (exploratory, not causal in MVP)?

## Deliverables

| Artifact | Location | Description |
|----------|----------|-------------|
| `clean_data` | `data/processed/clean_data.csv` | Merged, cleaned feature set |
| `agg_data` | `data/processed/agg_data.csv` | Monthly sales summary |
| Bronze copies | `data/bronze/` | Parquet snapshots of extracts |
| Documentation | `docs/` | Requirements, architecture, runbook |
