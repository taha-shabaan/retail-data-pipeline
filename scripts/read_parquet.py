from __future__ import annotations

from pathlib import Path
from pipeline.settings import load_settings

import pandas as pd

settings = load_settings()
RAW = settings.raw_dir
EXTRA_DATA_PATH = settings.extra_data_path
# EXTRA_DATA_COLUMNS = settings.extra_data_columns
# Rows align with docker/init/02_seed.sql store-weeks; multiple departments per store-week.



def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    df = pd.read_parquet(
        EXTRA_DATA_PATH,
    )
    print(df.head())
    print(df.tail())
    print(df.shape)
    # convert the Date column to a datetime object))


if __name__ == "__main__":
    main()
