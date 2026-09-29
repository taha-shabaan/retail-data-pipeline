# LinkedIn draft — Post 6: What I’d add in production

**Hook:** MVP pipelines prove thinking; production pipelines prove restraint—you add only what failures taught you to need.

**Body:**
- Schedule `pipeline/run_batch.py` in Airflow/Dagster with SLAs by mart.
- Secrets manager for Postgres; no passwords in compose for real envs.
- Metrics: rows in/out per stage, duration, data freshness per mart.
- Incremental extract watermarks; backfill runbook already started in `docs/runbook.md`.

**CTA:** Invite DMs on retail modeling or batch design—link repo again.

**Tradeoff:** I deliberately did not deploy orchestration here—recruiters see the seam where I’d plug it in, not a black-box template.
