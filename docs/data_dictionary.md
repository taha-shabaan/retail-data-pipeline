# Data dictionary

## Operational (PostgreSQL)

### `operational.stores`

| Column | Type | Description |
|--------|------|-------------|
| store_id | integer | Surrogate key |
| store_name | text | Display name |
| state_code | char(2) | US state |
| opened_date | date | Store open date |

### `operational.products`

| Column | Type | Description |
|--------|------|-------------|
| product_id | integer | Surrogate key |
| product_name | text | SKU description |
| category | text | Default category |
| unit_price | numeric | Current list price |

### `operational.transaction_lines`

| Column | Type | Description |
|--------|------|-------------|
| line_id | bigint | Line surrogate key |
| transaction_id | bigint | Basket / receipt id |
| store_id | integer | FK → stores |
| product_id | integer | FK → products |
| sale_date | date | Business sale date |
| quantity | integer | Units sold (> 0) |
| unit_price | numeric | Price at time of sale |

**Grain:** one row per line item.

## Parquet supplement (`data/raw/product_supplement.parquet`)

| Column | Type | Description |
|--------|------|-------------|
| product_id | int64 | Join key to products |
| category_override | string | Optional category correction from file feed |
| is_promotional | bool | Promo flag from partner file |

## Silver

### `fct_sales`

Line-level fact with `line_revenue = quantity * unit_price`.

### `dim_store`, `dim_product`

Conformed dimensions after enrich/join rules.

## Gold marts

### `mart_daily_store_sales`

| Grain | Columns (core) |
|-------|----------------|
| sale_date + store_id | total_revenue, units_sold, transaction_count, store attributes |

### `mart_product_performance`

| Grain | Columns (core) |
|-------|----------------|
| product_id | total_revenue, units_sold, store_count, product attributes |
