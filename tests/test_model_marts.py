from model.marts.build import build_gold_marts
from transform.quality.checks import build_silver


def test_mart_daily_store_sales_grain(
    sample_stores, sample_products, sample_lines, sample_supplement
):
    silver = build_silver(sample_stores, sample_products, sample_lines, sample_supplement)
    marts = build_gold_marts(silver)
    daily = marts["mart_daily_store_sales"]
    assert daily.height == 2
    assert set(daily.columns) >= {
        "sale_date",
        "store_id",
        "total_revenue",
        "units_sold",
        "transaction_count",
        "store_name",
    }
