# LinkedIn draft — Post 1: Architecture + repo map

**Hook:** I’m building a retail data pipeline inspired by Walmart-style operations—SQL for live stores and sales, Parquet for partner files, one batch path to marts analysts can query in minutes.

**Body:**
- Why batch ETL still matters for retail reporting (daily store performance, category mix).
- Two sources, one contract: everything lands in bronze before we trust it.
- Repo map: `ingest/` → `transform/` → `model/` → `load/` + tests and CI.

**CTA:** GitHub link — README has the diagram and quick start.

**Tradeoff:** Batch, not streaming—for this portfolio I optimized for clarity and testability; real-time inventory would be a second pipeline.
