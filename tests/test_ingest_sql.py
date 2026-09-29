import os

import pytest

from ingest.sql.postgres import extract_table
from pipeline.settings import load_settings

pytestmark = pytest.mark.skipif(
    os.getenv("CI") != "true" and not os.getenv("RUN_SQL_INTEGRATION"),
    reason="PostgreSQL integration test (set RUN_SQL_INTEGRATION=1 or run in CI)",
)


def test_extract_stores():
    settings = load_settings()
    df = extract_table(settings, "stores")
    assert df.height >= 3
