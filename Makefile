.PHONY: setup up down seed pipeline test lint fmt help

export PYTHONPATH := $(CURDIR)

help:
	@echo "Targets: setup | up | down | seed | pipeline | test | lint | fmt"

setup:
	python3 -m venv .venv
	.venv/bin/pip install -U pip
	.venv/bin/pip install -e ".[dev]"

up:
	docker compose -f docker/compose.yml up -d

down:
	docker compose -f docker/compose.yml down

seed: up
	@echo "Waiting for Postgres..."
	@sleep 3
	.venv/bin/python scripts/generate_sample_parquet.py

pipeline:
	.venv/bin/python pipeline/run_batch.py

test:
	pytest -q

lint:
	ruff check ingest transform model load pipeline tests scripts
	ruff format --check ingest transform model load pipeline tests scripts

fmt:
	ruff format ingest transform model load pipeline tests scripts
