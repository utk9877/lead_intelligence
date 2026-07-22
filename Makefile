.PHONY: sync up down logs test lint fmt typecheck migrate seed

sync:            ## Install/refresh the whole uv workspace
	uv sync --all-packages

up:              ## Start the local stack (Postgres + MinIO)
	docker compose up -d

down:            ## Stop the local stack
	docker compose down

logs:            ## Tail local stack logs
	docker compose logs -f

test: sync       ## Run all tests
	uv run pytest

lint: sync       ## Ruff lint + format check + mypy
	uv run ruff check .
	uv run ruff format --check .
	uv run mypy libs services

fmt: sync        ## Auto-format
	uv run ruff format .
	uv run ruff check --fix .

typecheck: sync  ## mypy only
	uv run mypy libs services

migrate:         ## Alembic migrations (lands in build chunk 1)
	@echo "not yet available: li-db/Alembic arrives in build chunk 1"

seed:            ## Seed fictional dev companies (lands in build chunk 6)
	@echo "not yet available: tools/seed.py arrives in build chunk 6"
