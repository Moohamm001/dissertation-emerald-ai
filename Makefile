.DEFAULT_GOAL := help
SHELL := /bin/bash

# Tools
UV ?= uv
PY ?= python
PYTEST ?= pytest
RUFF ?= ruff
BLACK ?= black
MYPY ?= mypy

# ─────────────────────────────────────────────────────────────
.PHONY: help
help:  ## Show this help
	@awk 'BEGIN {FS = ":.*##"; printf "\nEMERALD-AI — make targets:\n\n"} \
		/^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2 } \
		/^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) }' $(MAKEFILE_LIST)

##@ Setup
.PHONY: install install-all
install:  ## Install runtime + dev deps
	$(UV) sync --extra dev

install-all:  ## Install everything (ml, dl, xai, mlops, api, docs, dev)
	$(UV) sync --extra all

.PHONY: setup-hooks
setup-hooks:  ## Install pre-commit git hooks
	pre-commit install

##@ Quality
.PHONY: lint format typecheck check
lint:  ## Run ruff + black --check
	$(RUFF) check src tests api
	$(BLACK) --check src tests api

format:  ## Auto-format code (ruff + black)
	$(RUFF) check --fix src tests api
	$(BLACK) src tests api

typecheck:  ## Run mypy in strict mode
	$(MYPY) src

check: lint typecheck test  ## All quality gates

##@ Tests
.PHONY: test test-fast test-cov
test:  ## Run full pytest suite with coverage
	$(PYTEST)

test-fast:  ## Run only fast tests (skip slow + integration)
	$(PYTEST) -m "not slow and not integration"

test-cov:  ## Run tests with HTML coverage report
	$(PYTEST) --cov-report=html
	@echo "Open htmlcov/index.html"

##@ Pipeline
.PHONY: eda preprocess train evaluate explain audit reproduce
eda:  ## Run exploratory data analysis (will populate notebooks/eda outputs)
	@echo "TODO: wire to src/emerald_ai/cli.py eda"

preprocess:  ## Build the preprocessing pipeline + feature catalogue
	@echo "TODO: wire to src/emerald_ai/cli.py preprocess"

train:  ## Train all six model families under nested CV
	@echo "TODO: wire to src/emerald_ai/cli.py train --all"

evaluate:  ## Compute metrics + calibration + conformal intervals
	@echo "TODO: wire to src/emerald_ai/cli.py evaluate"

explain:  ## Generate SHAP + counterfactual + fidelity reports
	@echo "TODO: wire to src/emerald_ai/cli.py explain"

audit:  ## Fairness + robustness + drift audit
	@echo "TODO: wire to src/emerald_ai/cli.py audit"

reproduce: preprocess train evaluate explain audit  ## End-to-end pipeline (≤ 8h target)

##@ Authoring
.PHONY: proposal literature
proposal:  ## Rebuild the dissertation proposal docx from the python-docx script
	cd docs/proposal && $(PY) build_proposal.py

literature:  ## Regenerate literature/papers/*.md from build_papers.py
	cd literature && $(PY) build_papers.py

##@ Research automation
.PHONY: research research-force research-status research-graph
research:  ## Run a research-engine sweep (implements research_automation.txt)
	emerald research run

research-force:  ## Re-process every paper even if already analysed
	emerald research run --force

research-status:  ## Show current brain state (counts + last-run timestamp)
	emerald research status

research-graph:  ## Emit citation graph as Graphviz DOT
	emerald research graph

##@ Application
.PHONY: api web docker-up docker-down
api:  ## Run FastAPI dev server (reload on change)
	uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

web:  ## Run React dev server
	cd web && pnpm dev

docker-up:  ## Start full stack via docker-compose
	docker compose up --build

docker-down:  ## Stop full stack
	docker compose down

##@ Housekeeping
.PHONY: clean clean-all
clean:  ## Remove caches + build artefacts (keeps .venv and data)
	rm -rf .pytest_cache .mypy_cache .ruff_cache .coverage htmlcov coverage.xml
	rm -rf build dist *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete

clean-all: clean  ## Remove .venv too
	rm -rf .venv
