.PHONY: setup up down seed pipeline results test lint fmt help

export PYTHONPATH := $(CURDIR)

help:
	@echo "Targets: setup | up | down | seed | pipeline | results | test | lint | fmt"

setup:
	python3 -m venv .venv
	.venv/bin/pip install -U pip
	.venv/bin/pip install -e ".[dev]"

up:
	docker compose -f docker/compose.yml up -d

down:
	docker compose -f docker/compose.yml down

seed: up
	.venv/bin/python scripts/seed_postgres.py
	.venv/bin/python scripts/generate_sample_parquet.py

pipeline:
	.venv/bin/python pipeline/run_batch.py

results:
	.venv/bin/python scripts/render_results.py

test:
	pytest -q

lint:
	ruff check ingest transform analysis load pipeline tests scripts
	ruff format --check ingest transform analysis load pipeline tests scripts

fmt:
	ruff format ingest transform analysis load pipeline tests scripts
