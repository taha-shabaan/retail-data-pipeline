CREATE SCHEMA IF NOT EXISTS walmart;

CREATE TABLE IF NOT EXISTS walmart.grocery_sales (
    "index"        INTEGER PRIMARY KEY,
    "Store_ID"     INTEGER NOT NULL,
    "Date"         DATE NOT NULL,
    "Dept"         INTEGER NOT NULL,
    "Weekly_Sales" NUMERIC(14, 2) CHECK ("Weekly_Sales" IS NULL OR "Weekly_Sales" >= 0)
);

CREATE INDEX IF NOT EXISTS idx_grocery_sales_date ON walmart.grocery_sales ("Date");
CREATE INDEX IF NOT EXISTS idx_grocery_sales_store ON walmart.grocery_sales ("Store_ID");
CREATE INDEX IF NOT EXISTS idx_grocery_sales_store_date_dept ON walmart.grocery_sales ("Store_ID", "Date", "Dept");
