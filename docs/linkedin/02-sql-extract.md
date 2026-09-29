# LinkedIn draft — Post 2: SQL extract

**Hook:** Your operational database is still the spine of retail analytics—if extract is sloppy, every dashboard lies politely.

**Body:**
- PostgreSQL in Docker as a stand-in for corporate RDBMS.
- Versioned SQL in `ingest/sql/queries/` (stores, products, transaction_lines).
- Python only handles connections, batch id, and bronze writes—not hidden logic in strings everywhere.

**CTA:** Folder tour + sample query file.

**Tradeoff:** Docker adds friction; it buys a credible “I’ve wired real SQL extract” story for recruiters.
