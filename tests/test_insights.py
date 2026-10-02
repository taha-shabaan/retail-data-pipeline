import pandas as pd

from analysis.insights import build_insights


def test_build_insights_peak_and_holiday_lift():
    clean = pd.DataFrame(
        {
            "IsHoliday": [0, 0, 1, 1],
            "Weekly_Sales": [100.0, 100.0, 150.0, 150.0],
            "Month": [2.0, 3.0, 11.0, 12.0],
        }
    )
    agg = pd.DataFrame(
        {
            "Month": [2.0, 3.0, 11.0, 12.0],
            "Weekly_Sales": [100.0, 120.0, 140.0, 200.0],
        }
    )
    insights = build_insights(clean, agg)
    assert insights.row_count_clean == 4
    assert insights.peak_month == 12
    assert insights.peak_month_label == "Dec"
    assert insights.peak_avg_weekly_sales == 200.0
    assert insights.holiday_lift_pct == 50.0
