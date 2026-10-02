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
    schema: str
    table: str


@dataclass(frozen=True)
class PipelineSettings:
    batch_id: str
    data_root: Path
    raw_dir: Path
    bronze_dir: Path
    processed_dir: Path
    postgres: PostgresSettings
    grocery_sales_filename: str
    extra_data_filename: str
    clean_data_csv_name: str
    agg_data_csv_name: str
    results_chart_png_name: str
    results_chart_docs_path: Path
    # extra_data_columns: list[str]

    @property
    def extra_data_path(self) -> Path:
        return self.raw_dir / self.extra_data_filename

    @property
    def clean_data_path(self) -> Path:
        return self.processed_dir / self.clean_data_csv_name

    @property
    def agg_data_path(self) -> Path:
        return self.processed_dir / self.agg_data_csv_name

    @property
    def results_chart_path(self) -> Path:
        return self.processed_dir / self.results_chart_png_name


def load_settings(config_path: Path | None = None) -> PipelineSettings:
    load_dotenv()
    root = Path(__file__).resolve().parents[1]
    config_path = config_path or root / "config" / "settings.yaml"
    with config_path.open(encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    batch_id = os.getenv("BATCH_ID", raw["project"]["batch_id"])

    # extra_data_columns = raw["parquet_sources"]["extra_data_columns"]
    # extra_data_columns = [column["name"] for column in extra_data_columns]


    def resolve_path(value: str) -> Path:
        path = Path(value)
        if path.is_absolute():
            return path
        return (root / path).resolve()

    pg = raw["postgres"]
    outputs = raw["outputs"]
    return PipelineSettings(
        batch_id=batch_id,
        data_root=resolve_path(os.getenv("DATA_ROOT", raw["paths"]["data_root"])),
        raw_dir=resolve_path(raw["paths"]["raw"]),
        bronze_dir=resolve_path(raw["paths"]["bronze"]),
        processed_dir=resolve_path(raw["paths"]["processed"]),
        postgres=PostgresSettings(
            host=os.getenv("POSTGRES_HOST", pg["host"]),
            port=int(os.getenv("POSTGRES_PORT", pg["port"])),
            database=os.getenv("POSTGRES_DB", pg["database"]),
            user=os.getenv("POSTGRES_USER", pg["user"]),
            password=os.getenv("POSTGRES_PASSWORD", "retail"),
            schema=pg["schema"],
            table=pg["table"],
        ),
        extra_data_filename=raw["parquet_sources"]["extra_data"],
        grocery_sales_filename=raw["sql_sources"]["grocery_sales"],
        clean_data_csv_name=outputs["clean_data_csv"],
        agg_data_csv_name=outputs["agg_data_csv"],
        results_chart_png_name=outputs["results_chart_png"],
        results_chart_docs_path=resolve_path(outputs["results_chart_docs"]),
    )


def ensure_data_dirs(settings: PipelineSettings) -> None:
    for directory in (settings.raw_dir, settings.bronze_dir, settings.processed_dir):
        directory.mkdir(parents=True, exist_ok=True)
