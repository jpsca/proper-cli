.PHONY: test
test:
	poetry run pytest -x src/proper_cli tests

.PHONY: lint
lint:
	poetry run flake8 src/proper_cli tests

.PHONY: coverage
coverage:
	poetry run pytest --cov-config=pyproject.toml --cov-report html --cov proper_cli src/proper_cli tests

.PHONY: types
types:
	poetry run pyright src/proper_cli

.PHONY: install
install:
	poetry install --with dev,test
	poetry run pre-commit install
