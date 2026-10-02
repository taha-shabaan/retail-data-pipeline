import pandas as pd

from ingest.parquet import reader
from ingest.sql import postgres
from pipeline.settings import load_settings


def merge_extra_data(
    store_data: pd.DataFrame,
    parquet_data: pd.DataFrame,
) -> pd.DataFrame:
    """Merge grocery sales with additional store/date data."""

    merged_data = store_data.merge(
        parquet_data,
        # on=["Store_ID", "Date"],
        # how="left",
    )

    return merged_data


def main():
    settings = load_settings()

    grocery_sales = postgres.extract_grocery_sales(settings)
    extra_data = reader.read_extra_data(settings)

    merged_data = merge_extra_data(
        grocery_sales,
        extra_data,
    )

    print(merged_data.columns)


if __name__ == "__main__":
    main()

