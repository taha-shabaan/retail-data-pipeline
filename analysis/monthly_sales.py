from __future__ import annotations

import pandas as pd


def build_agg_data(clean_data: pd.DataFrame) -> pd.DataFrame:
    """
    Preliminary analysis: average weekly sales by calendar month.

    Matches the project deliverable `agg_data` (Month, Weekly_Sales).
    """
    agg_data = (
        clean_data.groupby("Month", as_index=False)["Weekly_Sales"]
        .mean()
        .sort_values("Month")
        .reset_index(drop=True)
    )
    agg_data["Month"] = agg_data["Month"].astype(float)
    return agg_data
