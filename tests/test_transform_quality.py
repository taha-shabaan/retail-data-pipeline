import polars as pl

from transform.quality.checks import build_silver


def test_build_silver_computes_line_revenue(
    sample_stores, sample_products, sample_lines, sample_supplement
):
    silver = build_silver(sample_stores, sample_products, sample_lines, sample_supplement)
    revenue = silver["fct_sales"].select("line_revenue").to_series().to_list()
    assert revenue == [9.96, 12.47]
    category = (
        silver["dim_product"].filter(pl.col("product_id") == 1002).select("category").item()
    )
    assert category == "Household Essentials"
