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
	uv run mypy libs services tools

fmt: sync        ## Auto-format
	uv run ruff format .
	uv run ruff check --fix .

typecheck: sync  ## mypy only
	uv run mypy libs services tools

migrate: sync    ## Apply Alembic migrations to the database in DATABASE_URL
	uv run alembic -c libs/db/alembic.ini upgrade head

api: sync        ## Run the FastAPI app locally (needs make up + make migrate first)
	uv run uvicorn li_api.main:app --reload --port 8000

console:         ## Run the Next.js QA console dev server (needs npm install first)
	cd services/qa-console && npm run dev

seed: sync       ## Seed fictional dev companies (needs make up + make migrate first)
	uv run python tools/seed.py

cost-report: sync ## Print the cost-per-account report from the ledger
	uv run python tools/cost_report.py
