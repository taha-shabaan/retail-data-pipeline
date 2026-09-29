from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import yaml
from dotenv import load_dotenv


@dataclass(frozen=True)
class PostgresSettings:
    host: str
    port: int
    database: str
    user: str
    password: str


@dataclass(frozen=True)
class PipelineSettings:
    batch_id: str
    data_root: Path
    raw_dir: Path
    bronze_dir: Path
    silver_dir: Path
    gold_dir: Path
    duckdb_path: Path
    postgres: PostgresSettings
    product_supplement_filename: str


def load_settings(config_path: Path | None = None) -> PipelineSettings:
    load_dotenv()
    root = Path(__file__).resolve().parents[1]
    config_path = config_path or root / "config" / "settings.yaml"
    with config_path.open(encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    batch_id = os.getenv("BATCH_ID", raw["project"]["batch_id"])

    def resolve_path(value: str) -> Path:
        path = Path(value)
        if path.is_absolute():
            return path
        return (root / path).resolve()

    data_root = resolve_path(os.getenv("DATA_ROOT", raw["paths"]["data_root"]))

    pg = raw["postgres"]
    return PipelineSettings(
        batch_id=batch_id,
        data_root=data_root,
        raw_dir=resolve_path(raw["paths"]["raw"]),
        bronze_dir=resolve_path(raw["paths"]["bronze"]),
        silver_dir=resolve_path(raw["paths"]["silver"]),
        gold_dir=resolve_path(raw["paths"]["gold"]),
        duckdb_path=resolve_path(raw["paths"]["duckdb"]),
        postgres=PostgresSettings(
            host=os.getenv("POSTGRES_HOST", pg["host"]),
            port=int(os.getenv("POSTGRES_PORT", pg["port"])),
            database=os.getenv("POSTGRES_DB", pg["database"]),
            user=os.getenv("POSTGRES_USER", pg["user"]),
            password=os.getenv("POSTGRES_PASSWORD", "retail"),
        ),
        product_supplement_filename=raw["parquet_sources"]["product_supplement"],
    )


def ensure_data_dirs(settings: PipelineSettings) -> None:
    for directory in (
        settings.raw_dir,
        settings.bronze_dir,
        settings.silver_dir,
        settings.gold_dir,
        settings.duckdb_path.parent,
    ):
        directory.mkdir(parents=True, exist_ok=True)
