# Pipeline steps (end-to-end)

Senior data engineering view of **what happens, in order**, and **why each step exists**. Implementation lives under `ingest/`, `transform/`, `analysis/`, and `load/`.

## Step 0 — Environment and sources

| Action | Detail |
|--------|--------|
| Start PostgreSQL | `make up` → Docker Compose service `postgres` on port **15432** |
| Place Parquet | `make seed` → writes `data/raw/extra_data.parquet` and loads SQL seed |
| Configure | Copy `.env.example` → `.env` if you override host/port |

**Why:** Recruiters and teammates should reproduce the run without guessing paths. Postgres holds **system of record** sales; Parquet holds **enrichment** that often arrives from vendors or the lake.

---

## Step 1 — Extract SQL (`grocery_sales`)

| Item | Detail |
|------|--------|
| Module | `ingest/sql/postgres.py` |
| Query | `ingest/sql/queries/grocery_sales.sql` |
| Source table | `walmart.grocery_sales` |

Columns: `"index"`, `"Store_ID"`, `"Date"`, `"Weekly_Sales"`.

**Output:** pandas DataFrame → bronze snapshot `data/bronze/.../sql/grocery_sales.parquet`.

**Why:** Versioned SQL keeps extract logic reviewable in PRs, separate from Python.

---

## Step 2 — Extract Parquet (`extra_data`)

| Item | Detail |
|------|--------|
| Module | `ingest/parquet/reader.py` |
| File | `data/raw/extra_data.parquet` (also mounted in container at `/data/raw/`) |

Validates expected columns (holiday flag, macro series, markdowns, `Dept`, `Size`, `Type`).

**Output:** pandas DataFrame → bronze `.../parquet/extra_data.parquet`.

**Why:** Fail fast on schema drift before you merge bad rows into `clean_data`.

---

## Step 3 — Merge and clean → `clean_data`

| Item | Detail |
|------|--------|
| Module | `transform/walmart_clean.py` |
| Join keys | `Store_ID`, `Date` |
| Derivation | `Month` = calendar month from `Date` |

**Output columns (contract):**

- `Store_ID`, `Month`, `Dept`, `IsHoliday`, `Weekly_Sales`, `CPI`, `Unemployment`

**Rules:**

- Inner join — only store-weeks present in **both** sources.
- Drop rows missing `Weekly_Sales`, `CPI`, or `Unemployment`.

**Why:** One explicit grain for holiday/supply analysis: store × week × department with shared weekly sales from SQL.

---

## Step 4 — Preliminary analysis → `agg_data`

| Item | Detail |
|------|--------|
| Module | `analysis/monthly_sales.py` |
| Logic | Group by `Month`, **mean** of `Weekly_Sales` |

**Output shape:**

| Month | Weekly_Sales |
|-------|--------------|
| 1.0 | … |
| 2.0 | … |

**Why:** Leadership-friendly first view before deeper seasonality or holiday-only filters. Swap to `sum` or weighted logic in phase 2 if finance defines monthly revenue differently.

---

## Step 5 — Load (publish CSV)

| Item | Detail |
|------|--------|
| Module | `load/csv_export.py` |
| Files | `data/processed/clean_data.csv`, `data/processed/agg_data.csv` |

**Why:** CSV keeps handoff simple for Excel, QuickSight, or course autograder-style checks.

---

## Step 5b — Results chart (portfolio / BI preview)

| Item | Detail |
|------|--------|
| Modules | `analysis/insights.py`, `analysis/results_chart.py` |
| Outputs | `data/processed/monthly_avg_weekly_sales.png`, `docs/assets/monthly_avg_weekly_sales.svg` |
| Refresh only | `make results` (reads processed CSVs, no Postgres) |

**Why:** One visual + headline metrics (peak month, holiday lift) for README and LinkedIn without waiting on a full BI stack.

---

## Step 6 — Orchestration entrypoint

| Item | Detail |
|------|--------|
| Command | `make pipeline` → `pipeline/run_batch.py` |
| Order | Extract SQL → Extract Parquet → `clean_data` → `agg_data` → CSV |

**Production next step:** Wrap the same functions in a scheduled DAG with row-count checks and alerts.

---

## Quick reference diagram

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
