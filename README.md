# Retail Data Pipeline — Walmart holiday sales

Batch data pipeline for **supply and demand analysis around public holidays** at a Walmart-scale US retailer. It combines **weekly grocery sales** from **PostgreSQL** with **complementary Parquet** (`extra_data.parquet`), builds `clean_data`, runs a **monthly sales summary** (`agg_data`), exports **CSV** deliverables, and publishes a **results chart**.

Educational portfolio project — uses **sample data**, not Walmart proprietary feeds.

## Table of contents

| Section | Topics |
| -------- | -------- |
| [Business requirements](#business-requirements) | [Context](#context) · [Problem](#problem-statement) · [Objectives](#objectives) · [Stakeholders](#stakeholders) · [Scope](#scope-in) · [Phase 2](#scope-out--phase-2) · [Non-functional](#non-functional-requirements) · [Business questions](#key-business-questions) · [Deliverables](#deliverables) |
| [Implementation plan](#implementation-plan) | Architecture decisions and deliverables |
| [Data dictionary](#data-dictionary) | [PostgreSQL source](#postgresql--walmartgrocery_sales) · [Parquet source](#parquet--datarawextra_dataparquet) · [clean_data](#pipeline-output--clean_data) · [agg_data](#pipeline-output--agg_data) · [File locations](#file-locations) |
| [Pipeline steps](#pipeline-steps) | [Step 0–6](#step-0--environment-and-sources) · [Results chart](#step-5b--results-chart) · [Flow diagram](#quick-reference-diagram) |
| [Results](#results) | Chart, insights, `make results` |
| [Runbook](#runbook) | [Prerequisites](#prerequisites) · [First run](#first-run) · [Outputs](#outputs) · [Docker](#docker-services) · [Troubleshooting](#troubleshooting) · [CI](#ci) |
| [Stack](#stack) | Technology choices |
| [Repo map](#repo-map) | Module layout |
| [Quick start](#quick-start) | Setup commands |
| [Development](#development) | Test and lint |
| [License](#license) | MIT |

---

## Business requirements

### Context

Walmart is the largest retailer in the United States and continues to grow its **e-commerce** channel. By the end of **2022**, online sales reached roughly **$80 billion**, about **13%** of total company sales. Planning inventory, staffing, and promotions requires understanding **supply and demand**, especially around **public holidays** (Super Bowl, Labor Day, Thanksgiving, Christmas, and similar events) when customer traffic and basket sizes shift quickly.

### Problem statement

Analytics and merchandising teams need a **trusted, repeatable dataset** that combines:

1. **Weekly store sales** from the operational database (`grocery_sales` in PostgreSQL).
2. **Complementary context** from a partner file (`extra_data.parquet`): holidays, macro indicators (CPI, unemployment), fuel prices, markdowns, and store/department attributes.

Without a pipeline, analysts merge spreadsheets manually, miss schema changes, and produce inconsistent monthly views of performance.

### Objectives

| ID | Objective | Success measure |
| ---- | ----------- | ----------------- |
| O1 | Ingest both sources on a schedule (batch MVP: on demand) | Zero manual copy-paste for routine refreshes |
| O2 | Produce **`clean_data`** with a documented column set | Downstream notebooks/BI use one grain |
| O3 | Run **preliminary analysis** — monthly view of sales | **`agg_data`** published with pipeline |
| O4 | Persist outputs for stakeholders | `clean_data.csv` and `agg_data.csv` in `data/processed/` |
| O5 | Support holiday-focused analysis | `IsHoliday` and calendar month available in `clean_data` |

### Stakeholders

| Stakeholder | Need |
| ------------- | ------ |
| Merchandising / supply chain | Month and department-level sales vs holidays |
| Store operations | Store type/size context from Parquet |
| Data & analytics | Stable schemas, reproducible transforms |
| Leadership | Directional monthly sales trend (`agg_data`) |

### Scope (in)

- Extract `walmart.grocery_sales` from PostgreSQL (Docker).
- Extract `extra_data.parquet` from `data/raw/` (mounted in Docker at `/data/raw` for visibility).
- Merge on **`Store_ID`**, **`Date`**, and **`Dept`** (store × week × department).
- Derive **`Month`** from `Date`.
- Output columns for **`clean_data`**: `Store_ID`, `Month`, `Dept`, `IsHoliday`, `Weekly_Sales`, `CPI`, `Unemployment`.
- Aggregate to **`agg_data`**: `Month`, `Weekly_Sales` (mean weekly sales across rows in that month for this MVP).
- Export both frames to CSV and publish a results chart.

### Scope (out) — phase 2

- Real-time streaming or intraday e-commerce events.
- Production orchestration (Airflow/Dagster), data contracts service, and ML forecasting.
- Official Walmart datasets or proprietary feeds (this repo uses **sample** data for learning).

### Non-functional requirements

| Area | Requirement |
| ------ | ------------- |
| Reproducibility | `make seed && make pipeline` on a clean clone |
| Tooling | **pandas** for transform and analysis (project standard) |
| Secrets | Postgres password via `.env`, not committed |
| Documentation | Requirements, dictionary, pipeline steps, and runbook in this README |

### Key business questions

1. How do **average weekly sales** change by **calendar month**?
2. Which **months** show higher sales when **`IsHoliday`** weeks are included?
3. How do **CPI** and **Unemployment** align with monthly sales movement (exploratory, not causal in MVP)?

### Deliverables

| Artifact | Location | Description |
| ---------- | ---------- | ------------- |
| `clean_data` | `data/processed/clean_data.csv` | Merged, cleaned feature set |
| `agg_data` | `data/processed/agg_data.csv` | Monthly sales summary |
| Results chart | `docs/assets/monthly_avg_weekly_sales.svg`, `data/processed/monthly_avg_weekly_sales.png` | Seasonal view + headline metrics |
| Bronze copies | `data/bronze/` | Parquet snapshots of extracts |

---

## Implementation plan

Aligned with the **Walmart holiday grocery sales** project (PostgreSQL + `extra_data.parquet` → `clean_data` / `agg_data` CSVs).

| Decision | Choice |
| ---------- | -------- |
| Sources | `walmart.grocery_sales` (Postgres), `extra_data.parquet` |
| Processing | pandas merge, clean, aggregate |
| Infrastructure | Docker Compose: Postgres + read-only mount of `data/raw` |
| Deliverables | `clean_data.csv`, `agg_data.csv`, results chart |
| Quality | pytest on ingest, transform, and analysis |
| Orchestration | `pipeline/run_batch.py` (`make pipeline`) |

---

## Data dictionary

### PostgreSQL — `walmart.grocery_sales`

| Column | Type | Description |
| -------- | ------ | ------------- |
| index | integer | Row id from source export |
| Store_ID | integer | Store identifier |
| Date | date | Week of sales (reporting week) |
| Dept | integer | Department number |
| Weekly_Sales | numeric | Sales dollars for that store-week-department |

### Parquet — `data/raw/extra_data.parquet`

| Column | Type | Description |
| -------- | ------ | ------------- |
| Store_ID | integer | Store identifier (join key) |
| Date | date | Week date (join key) |
| IsHoliday | integer | 1 if week contains a public holiday, else 0 |
| Temperature | float | Temperature on day of sale |
| Fuel_Price | float | Regional fuel price |
| CPI | float | Consumer price index |
| Unemployment | float | Unemployment rate |
| MarkDown1 … MarkDown4 | float | Promotional markdown counts |
| Dept | integer | Department number in store (join key) |
| Size | integer | Store size metric |
| Type | string | Store type (related to Size) |

### Pipeline output — `clean_data`

| Column | Type | Description |
| -------- | ------ | ------------- |
| Store_ID | integer | Store |
| Month | float | Calendar month from `Date` |
| Dept | integer | Department |
| IsHoliday | integer | Holiday flag |
| Weekly_Sales | float | Store-week sales from SQL |
| CPI | float | Macro index |
| Unemployment | float | Macro rate |

### Pipeline output — `agg_data`

| Column | Type | Description |
| -------- | ------ | ------------- |
| Month | float | Calendar month |
| Weekly_Sales | float | Mean of `Weekly_Sales` in `clean_data` for that month |

### File locations

| Artifact | Path |
| ---------- | ------ |
| Raw Parquet | `data/raw/extra_data.parquet` |
| Bronze SQL extract | `data/bronze/batch_id=<id>/sql/grocery_sales.parquet` |
| Bronze Parquet extract | `data/bronze/batch_id=<id>/parquet/extra_data.parquet` |
| clean_data CSV | `data/processed/clean_data.csv` |
| agg_data CSV | `data/processed/agg_data.csv` |
| Results chart (SVG) | `docs/assets/monthly_avg_weekly_sales.svg` |
| Results chart (PNG) | `data/processed/monthly_avg_weekly_sales.png` |

---

## Pipeline steps

End-to-end view of **what happens, in order**, and **why each step exists**. Code lives under `ingest/`, `transform/`, `analysis/`, `load/`, and `pipeline/`.

### Step 0 — Environment and sources

| Action | Detail |
| -------- | -------- |
| Start PostgreSQL | `make up` → Docker Compose service `postgres` on port **15432** |
| Place Parquet | `make seed` → loads Postgres seed and ensures `data/raw/extra_data.parquet` |
| Configure | Copy `.env.example` → `.env` if you override host/port |

**Why:** Reproducible runs without guessing paths. Postgres is the **system of record** for sales; Parquet holds **enrichment** from vendors or the lake.

### Step 1 — Extract SQL (`grocery_sales`)

| Item | Detail |
| ------ | -------- |
| Module | `ingest/sql/postgres.py` |
| Query | `ingest/sql/queries/grocery_sales.sql` |
| Source table | `walmart.grocery_sales` |

**Output:** pandas DataFrame → bronze snapshot `data/bronze/.../sql/grocery_sales.parquet`.

**Why:** Versioned SQL keeps extract logic reviewable in PRs, separate from Python.

### Step 2 — Extract Parquet (`extra_data`)

| Item | Detail |
| ------ | -------- |
| Module | `ingest/parquet/reader.py` |
| File | `data/raw/extra_data.parquet` (container mount: `/data/raw/`) |

Validates expected columns (holiday flag, macro series, markdowns, `Dept`, `Size`, `Type`).

**Output:** pandas DataFrame → bronze `.../parquet/extra_data.parquet`.

**Why:** Fail fast on schema drift before merging bad rows into `clean_data`.

### Step 3 — Merge and clean → `clean_data`

| Item | Detail |
| ------ | -------- |
| Module | `transform/walmart_clean.py` |
| Join keys | `Store_ID`, `Date`, `Dept` |
| Derivation | `Month` = calendar month from `Date` |

**Rules:** Inner join; drop rows missing `Weekly_Sales`, `CPI`, or `Unemployment`.

**Why:** One explicit grain for holiday/supply analysis: store × week × department.

### Step 4 — Preliminary analysis → `agg_data`

| Item | Detail |
| ------ | -------- |
| Module | `analysis/monthly_sales.py` |
| Logic | Group by `Month`, **mean** of `Weekly_Sales` |

**Why:** Leadership-friendly first view before deeper seasonality or holiday-only filters.

### Step 5 — Load (publish CSV)

| Item | Detail |
| ------ | -------- |
| Module | `load/csv_export.py` |
| Files | `data/processed/clean_data.csv`, `data/processed/agg_data.csv` |

**Why:** Simple handoff for Excel, QuickSight, or portfolio review.

### Step 5b — Results chart

| Item | Detail |
| ------ | -------- |
| Modules | `analysis/insights.py`, `analysis/results_chart.py` |
| Outputs | PNG under `data/processed/`, SVG under `docs/assets/` |
| Refresh only | `make results` (reads processed CSVs, no Postgres) |

**Why:** One visual plus peak month and holiday lift for README and LinkedIn without a full BI stack.

### Step 6 — Orchestration entrypoint

| Item | Detail |
| ------ | -------- |
| Command | `make pipeline` → `pipeline/run_batch.py` |
| Order | Extract SQL → Extract Parquet → `clean_data` → `agg_data` → CSV → chart |

**Production next step:** Wrap the same functions in a scheduled DAG with row-count checks and alerts.

### Quick reference diagram

```
PostgreSQL (grocery_sales)     extra_data.parquet
         │                              │
         └──────────┬───────────────────┘
                    ▼
              merge + clean  →  clean_data
                    ▼
            monthly analysis  →  agg_data
                    ▼
              clean_data.csv / agg_data.csv
                    ▼
         results chart (PNG + SVG)
```

---

## Results

After `make pipeline`, the batch job writes CSVs under `data/processed/` and refreshes the chart below (also saved to `docs/assets/` for the repo).

![Average weekly grocery sales by calendar month](docs/assets/monthly_avg_weekly_sales.svg)

PNG for slides or LinkedIn: `data/processed/monthly_avg_weekly_sales.png` (after `make pipeline`).

| Insight | What it means |
| -------- | --------------- |
| **Monthly trend** | `agg_data` is the mean of `Weekly_Sales` across all store–department rows in each calendar month. |
| **Peak month** | Highlighted bar = month with the highest average weekly sales in the merged dataset. |
| **Holiday lift** | Mean sales in **holiday weeks** (`IsHoliday = 1`) vs **non-holiday weeks** — directional only, not causal. |
| **Grain** | Inner join on `Store_ID`, `Date`, and `Dept`; rows missing CPI/unemployment are dropped in transform. |

Regenerate the chart without re-querying Postgres (CSVs must exist):

```bash
make results
```

**Sample run (local data):** peak month **Dec**, holiday-week sales about **+7%** vs non-holiday weeks — see the chart footnote after `make pipeline` or `make results`.

---

## Runbook

### Prerequisites

- Docker
- Python 3.11+

### First run

```bash
cp .env.example .env
make setup
make seed      # docker up + Postgres seed + raw Parquet
make pipeline
```

Postgres listens on **15432** (avoids conflict with a local instance on 5432).

Verify:

```bash
head -5 data/processed/clean_data.csv
cat data/processed/agg_data.csv
make results   # optional: refresh chart from CSVs
```

### Outputs

| File | Description |
| ------ | ------------- |
| `data/processed/clean_data.csv` | Merged features |
| `data/processed/agg_data.csv` | Monthly mean weekly sales |
| `data/processed/monthly_avg_weekly_sales.png` | Results chart (PNG) |
| `docs/assets/monthly_avg_weekly_sales.svg` | Results chart (committed for README) |

Preview:

```bash
.venv/bin/python -c "import pandas as pd; print(pd.read_csv('data/processed/agg_data.csv'))"
```

### Docker services

| Service | Host port | Notes |
| --------- | ----------- | -------- |
| `postgres` | 15432 | Database `retail`, user/password `retail` |
| Parquet mount | — | Host `data/raw` → container `/data/raw` (read-only) |

### Troubleshooting

| Issue | Fix |
| ------- | ----- |
| Port 15432 in use | Change host port in `docker/compose.yml` and `config/settings.yaml` |
| `extra_data.parquet` missing | Run `make seed` |
| Empty `clean_data` | Confirm seed SQL dates match Parquet `Date` values |
| Auth failed on Postgres | Check `.env` matches Docker credentials |
| `ModuleNotFoundError: pipeline` | Run from repo root: `make setup` and use `make pipeline` (sets `PYTHONPATH`) or `pip install -e .` |

### CI

GitHub Actions applies `docker/init/*.sql`, generates Parquet, runs unit tests. Full pipeline integration runs when the Postgres service is available.

---

## Stack

| Area | Choice |
| ------ | -------- |
| SQL source | PostgreSQL 16 (Docker Compose) |
| File source | Parquet (`pyarrow`) |
| Transform & analysis | **pandas** |
| Visualization | **matplotlib** (PNG) + SVG export |
| Orchestration | `pipeline/run_batch.py` (`make pipeline`) |
| Quality | pytest on ingest, transform, analysis |

---

## Repo map

| Path | Role |
| ------ | ------ |
| [docker/](docker/) | Postgres + mount for `data/raw` Parquet |
| [ingest/sql/](ingest/sql/) | Extract `grocery_sales` |
| [ingest/parquet/](ingest/parquet/) | Extract `extra_data.parquet` |
| [transform/walmart_clean.py](transform/walmart_clean.py) | Merge → `clean_data` |
| [analysis/monthly_sales.py](analysis/monthly_sales.py) | `agg_data` |
| [analysis/insights.py](analysis/insights.py) | Peak month & holiday lift metrics |
| [analysis/results_chart.py](analysis/results_chart.py) | Results chart (SVG + PNG) |
| [load/csv_export.py](load/csv_export.py) | CSV deliverables |
| [pipeline/run_batch.py](pipeline/run_batch.py) | Batch orchestration |
| [config/settings.yaml](config/settings.yaml) | Paths, Postgres, output names |

---

## Quick start

```bash
cp .env.example .env
make setup
make seed
make pipeline
```

---

## Development

```bash
make test
make lint
make fmt
```

---

## License

MIT — [LICENSE](LICENSE).
