from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd
import sqlalchemy as sa

from pipeline.settings import PipelineSettings, load_settings

logger = logging.getLogger(__name__)

# get the path to the grocery_sales.sql query file
QUERY_PATH = Path(__file__).resolve().parent / "queries" / "grocery_sales.sql"


def _connect(settings: PipelineSettings) -> sa.Connection:
    # get the connection information from the settings
    pg = settings.postgres
    # create the connection string
    conninfo = (
        f"postgresql://{pg.user}:{pg.password}@{pg.host}:{pg.port}/{pg.database}"
    )
    # create the connection engine
    return sa.create_engine(conninfo).connect()


# extract the grocery_sales data from the PostgreSQL database
def extract_grocery_sales(settings: PipelineSettings) -> pd.DataFrame:
    # get the query from the query file

    # query = QUERY_PATH.read_text(encoding="utf-8")
    query = "SELECT * FROM walmart.grocery_sales;"
    print(query)
    # log the query
    logger.info("Extracting walmart.grocery_sales from PostgreSQL: %s", query)
    # connect to the database
    with _connect(settings) as conn:
        # read the query into a pandas dataframe
        df = pd.read_sql(query, conn)
    # log the number of rows extracted
    logger.info("Extracted %s grocery_sales rows", len(df))
    return df


# validate the grocery_sales dataframe
def write_bronze_grocery_sales(settings: PipelineSettings, df: pd.DataFrame) -> Path:
    # get the path to the output directory
    out_dir = settings.bronze_dir / f"batch_id={settings.batch_id}" / "sql"
    # create the output directory if it doesn't exist
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / settings.grocery_sales_filename
    df.to_csv(path, index=False)
    # log the path of the file that was written
    logger.info("Wrote bronze %s", path)
    # return the path of the file that was written
    return path

def main():
    settings = load_settings()
    df = extract_grocery_sales(settings)
    write_bronze_grocery_sales(settings, df)
    print(df.head())
    print(df.shape)
    print(df.columns)
    print(df.dtypes)
    print(df.info())
    print(df.describe())
    # print(df.corr())
    # print(df.cov())
    # print(df.skew())
    # print(df.kurt())
    # print(df.mad())

if __name__ == "__main__":
    main()