.PHONY: install
install:
	uv sync --all-groups
	uv run pre-commit install

.PHONY: test
test:
	uv run pytest -x src/proper_cli tests

.PHONY: lint
lint:
	uv run ruff check src/proper_cli tests
	uv run ty check

.PHONY: lintfix
lintfix:
	uv run ruff check src/proper_cli tests --fix

.PHONY: coverage
coverage:
	uv run pytest --cov-config=pyproject.toml --cov-report html --cov proper_cli src/proper_cli tests
