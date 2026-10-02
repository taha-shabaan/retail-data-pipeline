#!/usr/bin/env python3
"""Regenerate the results chart from processed CSVs (no database required)."""

from __future__ import annotations

import sys

import pandas as pd

from analysis.insights import build_insights
from analysis.results_chart import plot_monthly_avg_sales
from pipeline.settings import load_settings


def main() -> int:
    settings = load_settings()
    clean_path = settings.clean_data_path
    agg_path = settings.agg_data_path
    if not clean_path.is_file() or not agg_path.is_file():
        print(
            "Missing processed CSVs. Run: make pipeline",
            file=sys.stderr,
        )
        return 1

    clean_data = pd.read_csv(clean_path)
    agg_data = pd.read_csv(agg_path)
    insights = build_insights(clean_data, agg_data)
    plot_monthly_avg_sales(agg_data, insights, settings.results_chart_path)
    plot_monthly_avg_sales(agg_data, insights, settings.results_chart_docs_path)
    print(
        f"Wrote {settings.results_chart_path} and {settings.results_chart_docs_path} "
        f"(peak {insights.peak_month_label}, holiday lift {insights.holiday_lift_pct:+.1f}%)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
