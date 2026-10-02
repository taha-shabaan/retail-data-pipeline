import pandas as pd

from transform.walmart_clean import CLEAN_DATA_COLUMNS, build_clean_data


def test_build_clean_data_columns_and_month():
    grocery = pd.DataFrame(
        {
            "index": [1, 2],
            "Store_ID": [1, 1],
            "Date": ["2010-02-05", "2010-02-05"],
            "Dept": [1, 2],
            "Weekly_Sales": [1000.0, 500.0],
        }
    )
    extra = pd.DataFrame(
        {
            "Store_ID": [1, 1],
            "Date": ["2010-02-05", "2010-02-05"],
            "IsHoliday": [0, 0],
            "Temperature": [40.0, 40.0],
            "Fuel_Price": [2.5, 2.5],
            "CPI": [210.0, 210.0],
            "Unemployment": [8.0, 8.0],
            "MarkDown1": [0.0, 1.0],
            "MarkDown2": [0.0, 0.0],
            "MarkDown3": [0.0, 0.0],
            "MarkDown4": [0.0, 0.0],
            "Dept": [1, 2],
            "Size": [100, 100],
            "Type": ["A", "A"],
        }
    )
    clean = build_clean_data(grocery, extra)
    assert list(clean.columns) == CLEAN_DATA_COLUMNS
    assert len(clean) == 2
    assert clean["Month"].unique().tolist() == [2.0]
