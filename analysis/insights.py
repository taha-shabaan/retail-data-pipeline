from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from analysis.agg_data_utils import normalize_agg_data

MONTH_LABELS = {
    1: "Jan",
    2: "Feb",
    3: "Mar",
    4: "Apr",
    5: "May",
    6: "Jun",
    7: "Jul",
    8: "Aug",
    9: "Sep",
    10: "Oct",
    11: "Nov",
    12: "Dec",
}


@dataclass(frozen=True)
class PipelineInsights:
    """Headline metrics for README and stakeholder summaries."""

    row_count_clean: int
    peak_month: int
    peak_month_label: str
    peak_avg_weekly_sales: float
    holiday_avg_weekly_sales: float
    non_holiday_avg_weekly_sales: float
    holiday_lift_pct: float


def build_insights(clean_data: pd.DataFrame, agg_data: pd.DataFrame) -> PipelineInsights:
    """Derive peak month and holiday vs non-holiday sales lift from pipeline outputs."""
    agg_data = normalize_agg_data(agg_data)
    peak_row = agg_data.loc[agg_data["Weekly_Sales"].idxmax()]
    peak_month = int(peak_row["Month"])
    peak_avg = float(peak_row["Weekly_Sales"])

    holiday_avg = float(
        clean_data.loc[clean_data["IsHoliday"] == 1, "Weekly_Sales"].mean()
    )
    non_holiday_avg = float(
        clean_data.loc[clean_data["IsHoliday"] == 0, "Weekly_Sales"].mean()
    )
    if pd.isna(holiday_avg):
        holiday_avg = 0.0
    if pd.isna(non_holiday_avg):
        non_holiday_avg = 0.0

    if non_holiday_avg > 0:
        lift_pct = (holiday_avg / non_holiday_avg - 1.0) * 100.0
    else:
        lift_pct = 0.0

    return PipelineInsights(
        row_count_clean=len(clean_data),
        peak_month=peak_month,
        peak_month_label=MONTH_LABELS.get(peak_month, str(peak_month)),
        peak_avg_weekly_sales=peak_avg,
        holiday_avg_weekly_sales=holiday_avg,
        non_holiday_avg_weekly_sales=non_holiday_avg,
        holiday_lift_pct=lift_pct,
    )
