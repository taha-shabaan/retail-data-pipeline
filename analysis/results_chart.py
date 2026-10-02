from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape

import pandas as pd

from analysis.agg_data_utils import normalize_agg_data
from analysis.insights import MONTH_LABELS, PipelineInsights


def plot_monthly_avg_sales(
    agg_data: pd.DataFrame,
    insights: PipelineInsights,
    output_path: Path,
) -> Path:
    """Save a bar chart of mean weekly sales by calendar month (PNG or SVG)."""
    output_path = Path(output_path)
    agg_data = normalize_agg_data(agg_data)
    if output_path.suffix.lower() == ".svg":
        return _plot_monthly_avg_sales_svg(agg_data, insights, output_path)
    return _plot_monthly_avg_sales_png(agg_data, insights, output_path)


def _plot_monthly_avg_sales_svg(
    agg_data: pd.DataFrame,
    insights: PipelineInsights,
    output_path: Path,
) -> Path:
    """Render the monthly sales chart as SVG (no matplotlib required)."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plot_df = agg_data.sort_values("Month").copy()
    months = plot_df["Month"].astype(int).tolist()
    labels = [MONTH_LABELS[m] for m in months]
    values = plot_df["Weekly_Sales"].tolist()
    peak_month = insights.peak_month

    width, height = 920, 520
    margin_left, margin_bottom, margin_top = 72, 88, 72
    chart_w = width - margin_left - 32
    chart_h = height - margin_top - margin_bottom
    max_val = max(values) if values else 1.0
    bar_w = chart_w / max(len(values), 1) * 0.65
    gap = chart_w / max(len(values), 1)

    bars: list[str] = []
    for idx, (label, value, month) in enumerate(zip(labels, values, months)):
        x = margin_left + idx * gap + (gap - bar_w) / 2
        bar_h = (value / max_val) * chart_h if max_val else 0
        y = margin_top + chart_h - bar_h
        fill = "#ffc220" if month == peak_month else "#0071ce"
        stroke = "#e6a800" if month == peak_month else "#004f9a"
        bars.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w:.1f}" '
            f'height="{bar_h:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="1"/>'
        )
        bars.append(
            f'<text x="{x + bar_w / 2:.1f}" y="{height - 48}" '
            f'text-anchor="middle" font-size="12" fill="#333">{escape(label)}</text>'
        )

    y_ticks = 5
    grid_lines: list[str] = []
    for tick in range(y_ticks + 1):
        y = margin_top + chart_h - (tick / y_ticks) * chart_h
        val = max_val * tick / y_ticks
        grid_lines.append(
            f'<line x1="{margin_left}" y1="{y:.1f}" x2="{width - 24}" y2="{y:.1f}" '
            f'stroke="#dddddd" stroke-dasharray="4 4"/>'
        )
        grid_lines.append(
            f'<text x="{margin_left - 8}" y="{y + 4:.1f}" text-anchor="end" '
            f'font-size="11" fill="#555">${val:,.0f}</text>'
        )

    title = "Average weekly grocery sales by month"
    subtitle = "PostgreSQL grocery_sales + Parquet extra_data (inner merge)"
    note = (
        f"Peak: {insights.peak_month_label} (${insights.peak_avg_weekly_sales:,.0f} avg/week) · "
        f"Holiday weeks: {insights.holiday_lift_pct:+.1f}% vs non-holiday · "
        f"{insights.row_count_clean:,} store-week rows"
    )

    svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="100%" height="100%" fill="#fafafa"/>
  <text x="{width / 2:.1f}" y="36" text-anchor="middle" font-size="18" font-weight="bold" fill="#111">{escape(title)}</text>
  <text x="{width / 2:.1f}" y="58" text-anchor="middle" font-size="12" fill="#444">{escape(subtitle)}</text>
  {''.join(grid_lines)}
  {''.join(bars)}
  <text x="{margin_left - 40}" y="{margin_top + chart_h / 2:.1f}" transform="rotate(-90 {margin_left - 40} {margin_top + chart_h / 2:.1f})" text-anchor="middle" font-size="12" fill="#333">Mean weekly sales ($)</text>
  <text x="{width / 2:.1f}" y="{height - 16}" text-anchor="middle" font-size="11" fill="#333">{escape(note)}</text>
</svg>
"""
    output_path.write_text(svg, encoding="utf-8")
    return output_path


def _plot_monthly_avg_sales_png(
    agg_data: pd.DataFrame,
    insights: PipelineInsights,
    output_path: Path,
) -> Path:
    """Render the monthly sales chart as PNG (requires matplotlib)."""
    import matplotlib.pyplot as plt

    output_path.parent.mkdir(parents=True, exist_ok=True)
    plot_df = agg_data.sort_values("Month").copy()
    plot_df["MonthLabel"] = plot_df["Month"].astype(int).map(MONTH_LABELS)

    fig, ax = plt.subplots(figsize=(10, 5.5))
    bars = ax.bar(
        plot_df["MonthLabel"],
        plot_df["Weekly_Sales"],
        color="#0071ce",
        edgecolor="#004f9a",
        linewidth=0.6,
    )
    peak_idx = plot_df["Month"].astype(int).tolist().index(insights.peak_month)
    bars[peak_idx].set_color("#ffc220")
    bars[peak_idx].set_edgecolor("#e6a800")

    ax.set_title(
        "Average weekly grocery sales by month\n"
        "(PostgreSQL grocery_sales + Parquet extra_data, inner merge)",
        fontsize=12,
        fontweight="bold",
    )
    ax.set_xlabel("Calendar month")
    ax.set_ylabel("Mean weekly sales ($)")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _pos: f"${x:,.0f}"))
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    ax.spines[["top", "right"]].set_visible(False)

    note = (
        f"Peak: {insights.peak_month_label} (${insights.peak_avg_weekly_sales:,.0f} avg/week) · "
        f"Holiday weeks: {insights.holiday_lift_pct:+.1f}% vs non-holiday "
        f"({insights.row_count_clean:,} store-week rows)"
    )
    fig.text(0.5, 0.02, note, ha="center", fontsize=9, color="#333333")
    fig.tight_layout(rect=(0, 0.06, 1, 1))

    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return output_path
