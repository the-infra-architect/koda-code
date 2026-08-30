.PHONY: setup format lint type test build security audit check

setup:
	uv sync --python 3.11 --extra dev --locked

format:
	uv run ruff format src tests

lint:
	uv run ruff check src tests

type:
	uv run mypy src

test:
	uv run pytest --cov=koda_code --cov-report=term-missing --cov-report=xml

build:
	uv run python -m build

security:
	uv run bandit -q -ll -r src
	uv run python -m koda_code.security

audit:
	uv run pip-audit

check: lint type test build security audit
	uv run ruff format --check src tests
