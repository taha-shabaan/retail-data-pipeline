from __future__ import annotations

import logging
import sys

from analysis.insights import build_insights
from analysis.monthly_sales import build_agg_data
from analysis.results_chart import plot_monthly_avg_sales
from ingest.parquet.reader import read_extra_data, write_bronze_extra_data
from ingest.sql.postgres import extract_grocery_sales, write_bronze_grocery_sales
from load.csv_export import save_deliverables
from pipeline.logging_setup import configure_logging
from pipeline.settings import ensure_data_dirs, load_settings
from transform.walmart_clean import build_clean_data

logger = logging.getLogger(__name__)


def run() -> tuple[object, object]:
    configure_logging()
    settings = load_settings()
    ensure_data_dirs(settings)
    logger.info("Starting Walmart holiday sales pipeline batch_id=%s", settings.batch_id)

    grocery_sales = extract_grocery_sales(settings)
    write_bronze_grocery_sales(settings, grocery_sales)

    extra_data = read_extra_data(settings)
    write_bronze_extra_data(settings, extra_data)

    clean_data = build_clean_data(grocery_sales, extra_data)
    agg_data = build_agg_data(clean_data)

    save_deliverables(
        clean_data,
        agg_data,
        settings.clean_data_path,
        settings.agg_data_path,
    )

    insights = build_insights(clean_data, agg_data)
    chart_path = plot_monthly_avg_sales(
        agg_data, insights, settings.results_chart_path
    )
    plot_monthly_avg_sales(agg_data, insights, settings.results_chart_docs_path)
    logger.info(
        "Results chart: %s (peak %s, holiday lift %+.1f%%)",
        chart_path,
        insights.peak_month_label,
        insights.holiday_lift_pct,
    )

    logger.info("Pipeline finished — clean_data and agg_data CSVs ready")
    return clean_data, agg_data


if __name__ == "__main__":
    run()
    sys.exit(0)
