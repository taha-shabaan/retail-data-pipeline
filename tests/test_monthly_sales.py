import pandas as pd

from analysis.monthly_sales import build_agg_data


def test_build_agg_data_monthly_mean():
    clean = pd.DataFrame(
        {
            "Store_ID": [1, 1, 2],
            "Month": [2.0, 2.0, 3.0],
            "Dept": [1, 2, 1],
            "IsHoliday": [0, 1, 0],
            "Weekly_Sales": [100.0, 200.0, 300.0],
            "CPI": [210.0, 210.0, 211.0],
            "Unemployment": [8.0, 8.0, 7.5],
        }
    )
    agg = build_agg_data(clean)
    assert list(agg.columns) == ["Month", "Weekly_Sales"]
    feb = agg.loc[agg["Month"] == 2.0, "Weekly_Sales"].iloc[0]
    assert feb == 150.0
