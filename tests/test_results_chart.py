from pathlib import Path

import pandas as pd

from analysis.insights import build_insights
from analysis.results_chart import plot_monthly_avg_sales


def test_plot_monthly_avg_sales_writes_png(tmp_path: Path):
    clean = pd.DataFrame(
        {
            "IsHoliday": [0, 1],
            "Weekly_Sales": [1000.0, 1100.0],
            "Month": [1.0, 2.0],
        }
    )
    agg = pd.DataFrame({"Month": [1.0, 2.0], "Weekly_Sales": [1000.0, 1100.0]})
    insights = build_insights(clean, agg)
    out = tmp_path / "chart.svg"
    plot_monthly_avg_sales(agg, insights, out)
    assert out.is_file()
    text = out.read_text(encoding="utf-8")
    assert "<svg" in text and "Feb" in text
