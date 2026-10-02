from __future__ import annotations

import pandas as pd
# import datetime as dt

from ingest.sql.postgres import extract_grocery_sales
from ingest.parquet.reader import read_extra_data
from pipeline.settings import load_settings
# from pipeline.settings import 
CLEAN_DATA_COLUMNS = [
    "Store_ID",
    "Month", # datetime to month
    "Dept", # int
    "IsHoliday", # int
    "Weekly_Sales", # float
    "CPI", # float
    "Unemployment", # float
]


def build_clean_data(grocery_sales: pd.DataFrame, extra_data: pd.DataFrame) -> pd.DataFrame:
    """Merge SQL and Parquet sources; derive month; keep analysis-ready columns."""
    sales = grocery_sales.copy()
    extra = extra_data.copy()

    print("grocery_sales Date isna: ", sales["Date"].isna().sum())

    # sales["Date"] = pd.to_datetime(sales["Date"])
    # extra["Date"] = pd.to_datetime(extra["Date"])

    merged = sales.merge(
        extra
        # , on=["Store_ID", "Date", "Dept"], how="inner", validate="one_to_one"
    )

    # convert Date to datetime
    merged["Month"] = pd.to_datetime(merged["Date"]).dt.month.astype(int) # datetime to month
    
    # copy the columns to the clean_data dataframe
    clean_data = merged[CLEAN_DATA_COLUMNS].copy()

    clean_data["CPI"] = clean_data["CPI"].fillna(clean_data["CPI"].mean())
    clean_data["Unemployment"] = clean_data["Unemployment"].fillna(clean_data["Unemployment"].ffill())

    return clean_data.reset_index(drop=True)

# Sum nulls in the data
def sumNulls(clean_data: pd.DataFrame):
    # Print the number of nulls in each column
        for column in clean_data.columns:
            print(column,": ", clean_data[column].isna().sum())


def info_clean_data(clean_data: pd.DataFrame):
    print("Month: ", clean_data["Month"].isna().sum())

def main():
    settings_obj = load_settings()
    grocery_sales = extract_grocery_sales(settings_obj)
    extra_data = read_extra_data(settings_obj)
    clean_data= build_clean_data(grocery_sales, extra_data)

    info_clean_data(clean_data)
    # sumNulls(clean_data)


if __name__ == "__main__":
    main()
