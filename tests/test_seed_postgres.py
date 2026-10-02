"""Tests for Postgres seed CSV normalization."""

from __future__ import annotations

import pandas as pd

from scripts.seed_postgres import prepare_grocery_sales


def test_prepare_grocery_sales_drops_empty_sales_and_parses_dates() -> None:
    raw = pd.DataFrame(
        {
            "level_0": ["0", "1"],
            "index": [0, 1],
            "Store_ID": [1, 1],
            "Date": ["2010-02-05T00:00:00.000", "2010-02-05T00:00:00.000"],
            "Dept": [1, 2],
            "Weekly_Sales": ["24924.5", ""],
        }
    )
    out = prepare_grocery_sales(raw)
    assert len(out) == 1
    assert out.loc[0, "Weekly_Sales"] == 24924.5
    assert str(out.loc[0, "Date"]) == "2010-02-05"
