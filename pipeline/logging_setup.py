from __future__ import annotations

import logging.config
from pathlib import Path

import yaml


def configure_logging(config_path: Path | None = None) -> None:
    root = Path(__file__).resolve().parents[1]
    config_path = config_path or root / "config" / "logging.yaml"
    with config_path.open(encoding="utf-8") as f:
        logging.config.dictConfig(yaml.safe_load(f))
