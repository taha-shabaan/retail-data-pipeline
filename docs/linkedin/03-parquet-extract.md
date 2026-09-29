# LinkedIn draft — Post 3: Parquet extract

**Hook:** Not all retail data lives in Postgres—Parquet dumps from partners and lake exports are normal second sources.

**Body:**
- `product_supplement.parquet` enriches categories and promo flags.
- Schema validation on read—fail fast when columns drift.
- Same bronze → silver path as SQL extract.

**CTA:** Show validation error vs happy path (screenshot or log snippet).

**Tradeoff:** Strict schemas reject bad files early; in prod you’d quarantine bad rows instead of failing the whole batch (phase 2).
