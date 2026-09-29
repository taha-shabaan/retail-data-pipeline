from __future__ import annotations

import polars as pl
import pytest


@pytest.fixture
def sample_stores() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "store_id": [1, 2],
            "store_name": ["A", "B"],
            "state_code": ["AR", "TX"],
            "opened_date": ["2010-01-01", "2011-01-01"],
        }
    ).with_columns(pl.col("opened_date").str.to_date())


@pytest.fixture
def sample_products() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "product_id": [1001, 1002],
            "product_name": ["Milk", "Towels"],
            "category": ["Grocery", "Household"],
            "unit_price": [4.98, 12.47],
        }
    )


@pytest.fixture
def sample_lines() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "line_id": [1, 2],
            "transaction_id": [90001, 90002],
            "store_id": [1, 2],
            "product_id": [1001, 1002],
            "sale_date": ["2024-03-01", "2024-03-01"],
            "quantity": [2, 1],
            "unit_price": [4.98, 12.47],
        }
    ).with_columns(pl.col("sale_date").str.to_date())


@pytest.fixture
def sample_supplement() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "product_id": [1002],
            "category_override": ["Household Essentials"],
            "is_promotional": [False],
        }
    )
