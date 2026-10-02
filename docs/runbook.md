# Runbook

## Prerequisites

- Docker
- Python 3.11+

## First run

```bash
cp .env.example .env
make setup
make seed      # docker up + extra_data.parquet + Postgres seed
make pipeline
```

## Outputs

| File | Description |
|------|-------------|
| `data/processed/clean_data.csv` | Merged features |
| `data/processed/agg_data.csv` | Monthly mean weekly sales |

Preview:

```bash
.venv/bin/python -c "import pandas as pd; print(pd.read_csv('data/processed/agg_data.csv'))"
```

## Docker services

| Service | Host port | Notes |
|---------|-----------|--------|
| `postgres` | 15432 | Database `retail`, user/password `retail` |
| Parquet mount | — | Host `data/raw` → container `/data/raw` (read-only) |

Regenerate Parquet only:

```bash
.venv/bin/python scripts/generate_sample_parquet.py
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Port 15432 in use | Change host port in `docker/compose.yml` and `config/settings.yaml` |
| `extra_data.parquet` missing | Run `make seed` |
| Empty `clean_data` | Confirm seed SQL dates match Parquet `Date` values |
| Auth failed on Postgres | Check `.env` matches Docker credentials |

## CI

GitHub Actions applies `docker/init/*.sql`, generates Parquet, runs unit tests. Full pipeline integration runs when Postgres service is available.
