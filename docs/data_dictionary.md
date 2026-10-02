# Data dictionary

## PostgreSQL — `walmart.grocery_sales`

| Column | Type | Description |
|--------|------|-------------|
| index | integer | Row id from source export |
| Store_ID | integer | Store identifier |
| Date | date | Week of sales (reporting week) |
| Dept | integer | Department number |
| Weekly_Sales | numeric | Sales dollars for that store-week-department |

## Parquet — `data/raw/extra_data.parquet`

| Column | Type | Description |
|--------|------|-------------|
| Store_ID | integer | Store identifier (join key) |
| Date | date | Week date (join key) |
| IsHoliday | integer | 1 if week contains a public holiday, else 0 |
| Temperature | float | Temperature on day of sale |
| Fuel_Price | float | Regional fuel price |
| CPI | float | Consumer price index |
| Unemployment | float | Unemployment rate |
| MarkDown1 … MarkDown4 | float | Promotional markdown counts |
| Dept | integer | Department number in store |
| Size | integer | Store size metric |
| Type | string | Store type (related to Size) |

## Pipeline output — `clean_data`

| Column | Type | Description |
|--------|------|-------------|
| Store_ID | integer | Store |
| Month | float | Calendar month from `Date` |
| Dept | integer | Department |
| IsHoliday | integer | Holiday flag |
| Weekly_Sales | float | Store-week sales from SQL |
| CPI | float | Macro index |
| Unemployment | float | Macro rate |

## Pipeline output — `agg_data`

| Column | Type | Description |
|--------|------|-------------|
| Month | float | Calendar month |
| Weekly_Sales | float | Mean of `Weekly_Sales` in `clean_data` for that month |

## File locations

| Artifact | Path |
|----------|------|
| Raw Parquet | `data/raw/extra_data.parquet` |
| Bronze SQL extract | `data/bronze/batch_id=<id>/sql/grocery_sales.parquet` |
| Bronze Parquet extract | `data/bronze/batch_id=<id>/parquet/extra_data.parquet` |
| clean_data CSV | `data/processed/clean_data.csv` |
| agg_data CSV | `data/processed/agg_data.csv` |
