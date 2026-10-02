# Implementation plan

Aligned with the **Walmart holiday grocery sales** project (PostgreSQL + `extra_data.parquet` → `clean_data` / `agg_data` CSVs).

| Decision | Choice |
|----------|--------|
| Sources | `walmart.grocery_sales` (Postgres), `extra_data.parquet` |
| Processing | pandas merge, clean, aggregate |
| Infrastructure | Docker Compose: Postgres + read-only mount of `data/raw` |
| Deliverables | `clean_data.csv`, `agg_data.csv` |
| Documentation | [business-requirements.md](business-requirements.md), [pipeline-steps.md](pipeline-steps.md), [architecture.md](architecture.md) |

LinkedIn drafts under `docs/linkedin/` describe an earlier portfolio narrative; update posts to point at holiday-sales scope when publishing.
