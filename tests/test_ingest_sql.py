import os

import pytest

from ingest.sql.postgres import extract_grocery_sales
from pipeline.settings import load_settings

pytestmark = pytest.mark.skipif(
    os.getenv("CI") != "true" and not os.getenv("RUN_SQL_INTEGRATION"),
    reason="PostgreSQL integration (CI or RUN_SQL_INTEGRATION=1)",
)


def test_extract_grocery_sales():
    settings = load_settings()
    df = extract_grocery_sales(settings)
    assert len(df) >= 1
    assert "Weekly_Sales" in df.columns
