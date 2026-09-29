from __future__ import annotations

from pathlib import Path

import polars as pl

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    df = pl.DataFrame(
        {
            "product_id": [1002, 1003],
            "category_override": ["Household Essentials", "Consumer Electronics"],
            "is_promotional": [False, True],
        }
    )
    path = RAW / "product_supplement.parquet"
    df.write_parquet(path)
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
