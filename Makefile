.PHONY: tests

VIRTUAL_ENV ?= venv
REQUIREMENTS:=requirements.txt
PIP=$(VIRTUAL_ENV)/bin/pip
PYTHON=$(VIRTUAL_ENV)/bin/python
ISORT=$(VIRTUAL_ENV)/bin/isort
FLAKE8=$(VIRTUAL_ENV)/bin/flake8
BLACK=$(VIRTUAL_ENV)/bin/black
PYTEST=$(VIRTUAL_ENV)/bin/pytest
PYTHON_MAJOR_VERSION=3
PYTHON_MINOR_VERSION=10
PYTHON_VERSION=$(PYTHON_MAJOR_VERSION).$(PYTHON_MINOR_VERSION)
PYTHON_MAJOR_MINOR=$(PYTHON_MAJOR_VERSION)$(PYTHON_MINOR_VERSION)
PYTHON_WITH_VERSION=python$(PYTHON_VERSION)
SOURCES=divessi/ tests

$(VIRTUAL_ENV):
	$(PYTHON_WITH_VERSION) -m venv $(VIRTUAL_ENV)
	$(PIP) install -r $(REQUIREMENTS)

virtualenv: $(VIRTUAL_ENV)

tests: $(VIRTUAL_ENV)
	$(PYTEST) tests

lint/isort: $(VIRTUAL_ENV)
	$(ISORT) --check-only --diff $(SOURCES)

lint/flake8: $(VIRTUAL_ENV)
	$(FLAKE8) $(SOURCES)

lint/black: $(VIRTUAL_ENV)
	$(BLACK) --check $(SOURCES)

format/isort: $(VIRTUAL_ENV)
	$(ISORT) $(SOURCES)

format/black: $(VIRTUAL_ENV)
	$(BLACK) --verbose $(SOURCES)

lint: lint/isort lint/flake8 lint/black

format: format/isort format/black

clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type d -name "*.egg-info" -exec rm -r {} +

clean/all: clean
	rm -rf $(VIRTUAL_ENV)
