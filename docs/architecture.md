# Architecture

## Business driver

Walmart’s mix of **stores and e-commerce** makes **holiday and seasonal demand** a first-class planning input. This pipeline supports **supply and demand analysis** by joining **weekly grocery sales** (PostgreSQL) with **complementary Parquet** features (holidays, macro indicators, departments, store format).

See [business-requirements.md](business-requirements.md) for stakeholders and scope.

## System context

```
                    ┌─────────────────────────────────────┐
                    │         Docker Compose              │
                    │  ┌─────────────┐  /data/raw (ro)   │
                    │  │ PostgreSQL  │◄── extra_data     │
                    │  │ grocery_sales                  │
                    │  └──────┬──────┘                    │
                    └─────────┼──────────────────────────┘
                              │ JDBC / psycopg
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                    pipeline/run_batch.py                      │
│  ingest/sql ──► ingest/parquet ──► transform ──► analysis   │
│                                         │              │       │
│                                         ▼              ▼       │
│                                   clean_data      agg_data     │
│                                         └──────┬───────┘       │
│                                                ▼               │
│                                         load/csv_export        │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
              data/processed/clean_data.csv
              data/processed/agg_data.csv
```

## Components

| Layer | Responsibility | Technology |
|-------|----------------|------------|
| Source — SQL | Weekly store sales | PostgreSQL 16, schema `walmart` |
| Source — files | Holidays, CPI, unemployment, dept/store attrs | Parquet on host + volume mount |
| Bronze | Immutable extract snapshots | Parquet under `data/bronze/batch_id=…` |
| Transform | Join, typing, column contract | pandas |
| Analysis | Monthly aggregation | pandas |
| Serve | Analyst deliverables | CSV in `data/processed/` |

## Data flow and grain

| Stage | Grain | Notes |
|-------|--------|------|
| `grocery_sales` | Store × week | One `Weekly_Sales` per store per `Date` |
| `extra_data` | Store × week × dept | Multiple departments per store-week |
| `clean_data` | Store × week × dept | `Weekly_Sales` repeated per dept row from join |
| `agg_data` | Month | Mean `Weekly_Sales` across all `clean_data` rows in month |

## Design decisions

1. **pandas** — project standard for merge, cleaning, and aggregation; readable for portfolio and course alignment.
2. **Inner join** — guarantees every analytic row has both sales and context; left join would be phase 2 for data-quality quarantine.
3. **Docker Postgres + host Parquet** — SQL realism without uploading Parquet into the DB; Compose mounts `data/raw` so both sources are visible in the same stack.
4. **Bronze before transform** — supports replay and debugging (“what did extract look like on batch X?”).

## Security and operations

- Credentials: `POSTGRES_*` in `.env` (see `.env.example`).
- No PII in sample data; replace with governed datasets in production.
- Runbook: [runbook.md](runbook.md). Step-by-step: [pipeline-steps.md](pipeline-steps.md).

## Phase 2 extensions

- Orchestrator with SLA monitors on row counts and max(`Date`).
- Great Expectations/Soda on `clean_data` contract.
- Separate **e-commerce** fact table and unified customer view.
