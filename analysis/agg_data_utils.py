from __future__ import annotations

import pandas as pd


def normalize_agg_data(agg_data: pd.DataFrame) -> pd.DataFrame:
    """Ensure agg_data uses the documented `Weekly_Sales` column name."""
    df = agg_data.copy()
    if "Weekly_Sales" not in df.columns and "Agg_weekly_Sales" in df.columns:
        df = df.rename(columns={"Agg_weekly_Sales": "Weekly_Sales"})
    return df
