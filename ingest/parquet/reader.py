from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from pipeline.settings import PipelineSettings, load_settings

logger = logging.getLogger(__name__)

EXTRA_DATA_COLUMNS = [
    "Store_ID",
    "Date",
    "IsHoliday",
    "Temperature",
    "Fuel_Price",
    "CPI",
    "Unemployment",
    "MarkDown1",
    "MarkDown2",
    "MarkDown3",
    "MarkDown4",
    "Dept",
    "Size",
    "Type",
]


# read the extra_data.parquet file into a pandas dataframe
def read_extra_data(settings: PipelineSettings) -> pd.DataFrame:
    # get the path to the extra_data.parquet file
    path = settings.extra_data_path
    # check if the file exists
    if not path.exists():
        raise FileNotFoundError(
            f"Missing {path}. Run: make seed (writes extra_data.parquet and starts Postgres)"
        )
   #log the path of the file that is being read
    logger.info("Reading Parquet %s", path)
    # read the parquet file into a pandas dataframe
    df = pd.read_parquet(path)
    # return the dataframe
    return df


# write the dataframe to a csv file in the bronze directory
def write_bronze_extra_data(settings: PipelineSettings, df: pd.DataFrame) -> Path:  
    # get the path to the output directory
    out_dir = settings.bronze_dir / f"batch_id={settings.batch_id}" / "parquet"
    # create the output directory if it doesn't exist
    out_dir.mkdir(parents=True, exist_ok=True)
    # get the path to the output file
    path = out_dir / settings.extra_data_filename
    # write the dataframe to the output file as a csv
    df.to_csv(path, index=False)
    # log the path of the file that was written
    logger.info("Wrote bronze %s", path)
    # return the path of the file that was written
    return path


def main():
    settings = load_settings()
    df = read_extra_data(settings)
    write_bronze_extra_data(settings, df)
    print(df.head())
    print(df.shape)
    print(df.columns)
    print(df.dtypes)
    print(df.info())
    print(df.describe())
    print(df.corr())
    print(df.cov())
    print(df.skew())

if __name__ == "__main__":
    main()