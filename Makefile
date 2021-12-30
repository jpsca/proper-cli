.PHONY: test
test:
	pytest -x proper_cli tests

.PHONY: lint
lint:
	flake8 --config=setup.cfg proper_cli tests

.PHONY: coverage
coverage:
	pytest --cov-report html --cov proper_cli proper_cli tests

.PHONY: install
install:
	pip install -e .[test,dev]
	# pre-commit install --hook-type pre-push
