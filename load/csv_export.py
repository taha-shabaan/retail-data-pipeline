from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


def save_deliverables(
    clean_data: pd.DataFrame,
    agg_data: pd.DataFrame,
    clean_path: Path,
    agg_path: Path,
) -> None:
    clean_path.parent.mkdir(parents=True, exist_ok=True)
    clean_data.to_csv(clean_path, index=False)
    agg_data.to_csv(agg_path, index=False)
    logger.info("Wrote %s (%s rows)", clean_path, len(clean_data))
    logger.info("Wrote %s (%s rows)", agg_path, len(agg_data))
