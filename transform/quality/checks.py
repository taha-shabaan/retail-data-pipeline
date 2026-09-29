from __future__ import annotations

from pathlib import Path

import polars as pl
import yaml


def load_rules() -> dict:
    path = Path(__file__).resolve().parent / "rules.yaml"
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def assert_required_columns(df: pl.DataFrame, required: list[str], label: str) -> None:
    missing = set(required) - set(df.columns)
    if missing:
        raise ValueError(f"{label}: missing columns {sorted(missing)}")


def check_transaction_lines(df: pl.DataFrame) -> pl.DataFrame:
    rules = load_rules()["transaction_lines"]
    assert_required_columns(df, rules["required_columns"], "transaction_lines")
    if df.select(pl.col("quantity").min()).item() < rules["quantity_min"]:
        raise ValueError("transaction_lines: quantity must be >= 1")
    return df.with_columns(
        (pl.col("quantity") * pl.col("unit_price")).alias("line_revenue").cast(pl.Float64)
    )


def enrich_products(products: pl.DataFrame, supplement: pl.DataFrame) -> pl.DataFrame:
    rules = load_rules()["products"]
    assert_required_columns(products, rules["required_columns"], "products")
    enriched = products.join(supplement, on="product_id", how="left")
    return (
        enriched.with_columns(
            pl.coalesce([pl.col("category_override"), pl.col("category")]).alias(
                "category_resolved"
            )
        )
        .drop(["category", "category_override"])
        .rename({"category_resolved": "category"})
    )


def build_silver(
    stores: pl.DataFrame,
    products: pl.DataFrame,
    lines: pl.DataFrame,
    supplement: pl.DataFrame,
) -> dict[str, pl.DataFrame]:
    lines_checked = check_transaction_lines(lines)
    products_enriched = enrich_products(products, supplement)
    return {
        "dim_store": stores,
        "dim_product": products_enriched.select(
            "product_id", "product_name", "category", "unit_price", "is_promotional"
        ),
        "fct_sales": lines_checked,
    }
