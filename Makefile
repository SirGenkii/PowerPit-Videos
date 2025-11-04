# ==== TennisNeuralNetwork — automation ====

.DEFAULT_GOAL := help

SHELL := /bin/bash

PYTHON := python3
VENV := .venv
PY := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
REQS := requirements.txt

## help: Show available targets
.PHONY: help
help:
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z0-9_.-]+:.*##/ {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

## check-python: Ensure Python is available
.PHONY: check-python
check-python:
	@command -v $(PYTHON) >/dev/null 2>&1 || { echo "Python not found"; exit 1; }
	@$(PYTHON) -V

## venv: Create virtual environment
.PHONY: venv
venv: check-python
	@test -d $(VENV) || $(PYTHON) -m venv $(VENV)
	@$(PIP) install --upgrade pip | sed '/Requirement already satisfied/d'

## activate: Open a shell with the virtualenv enabled
.PHONY: activate
activate: ## Spawn a subshell with the venv activated
	@test -d $(VENV) || $(MAKE) venv
	@echo "Activating virtualenv: $(VENV)"
	@echo "Exit the shell to return to your normal environment."
	@bash --rcfile <(echo "source $(VENV)/bin/activate")

## install: Install project dependencies
.PHONY: install
install: venv ## Install project dependencies
	@set -o pipefail; \
	if [ -f $(REQS) ]; then \
		$(PIP) install -r $(REQS) | sed '/Requirement already satisfied/d'; \
	else \
		echo "No $(REQS) file found, skipping."; \
	fi

## freeze: Freeze current environment to requirements.txt
.PHONY: freeze
freeze: install ## Freeze current environment to requirements.txt
	@$(PIP) freeze > $(REQS)
	@echo "Wrote $(REQS)"
