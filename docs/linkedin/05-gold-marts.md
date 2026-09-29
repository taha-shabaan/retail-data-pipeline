# LinkedIn draft — Post 5: Star inside, wide tables outside

**Hook:** Interviewers ask about star schemas; analysts ask for one table they can filter—good pipelines deliver both.

**Body:**
- Silver: `fct_sales` at line grain + dims.
- Gold: `mart_daily_store_sales`, `mart_product_performance`.
- Load: DuckDB for demos + Parquet partitions for lake-style access.

**CTA:** Sample DuckDB query from runbook.

**Tradeoff:** Wide marts duplicate data; you accept storage for simpler BI and clearer ownership of grain.
