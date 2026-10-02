-- Load grocery_sales from datalab export (department-level weekly sales)
CREATE TEMP TABLE grocery_sales_staging (
    level_0        TEXT,
    "index"        INTEGER,
    "Store_ID"     INTEGER,
    "Date"         TEXT,
    "Dept"         INTEGER,
    "Weekly_Sales" TEXT
);

COPY groceryl_sales_staging
FROM '/docker-entrypoint-initdb.d/datalab_export_2026-09-29 17_47_06.csv'
WITH (FORMAT csv, HEADER true, NULL '');

INSERT INTO walmart.grocery_sales ("index", "Store_ID", "Date", "Dept", "Weekly_Sales")
SELECT
    s."index",
    s."Store_ID",
    (s."Date"::timestamptz AT TIME ZONE 'UTC')::date,
    s."Dept",
    NULLIF(TRIM(s."Weekly_Sales"), '')::numeric
FROM grocery_sales_staging AS s
WHERE NULLIF(TRIM(s."Weekly_Sales"), '') IS NOT NULL
  AND NULLIF(TRIM(s."Date"), '') IS NOT NULL;
