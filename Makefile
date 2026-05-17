# EMERALD-AI Makefile — thin wrapper around the Python CLI.
#
# Every target below delegates to `python -m emerald_ai <command>`. The CLI is
# the source of truth; this Makefile exists only as a convenience for Unix
# users who prefer typing `make test` over `python -m emerald_ai test`.
#
# Windows users can ignore this file entirely and use one of:
#     python emerald.py <command>       (zero-install launcher)
#     python -m emerald_ai <command>    (after pip install -e .)
#     emerald <command>                 (after install, Scripts on PATH)
#
# See `python emerald.py --help` for the full command list.

.DEFAULT_GOAL := help
PY ?= python

.PHONY: help install install-all setup-hooks lint format typecheck test test-fast \
        test-cov check eda preprocess train evaluate explain audit reproduce \
        proposal literature research research-force research-status research-graph \
        api web docker-up docker-down clean clean-all

help:  ## Show this help
	@awk 'BEGIN {FS = ":.*##"; printf "\nEMERALD-AI — make targets (Unix convenience wrappers):\n\n"} \
		/^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2 } \
		/^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) }' $(MAKEFILE_LIST)
	@echo ""
	@echo "Windows users: use 'python emerald.py <command>' or 'python -m emerald_ai <command>' instead."

##@ Setup
install:           ## Install runtime + dev deps (uv preferred, falls back to pip)
	@command -v uv >/dev/null 2>&1 && uv sync --extra dev --extra docs || pip install -e ".[dev,docs]"

install-all:       ## Install every optional extra (ml, dl, xai, mlops, api, docs, dev)
	@command -v uv >/dev/null 2>&1 && uv sync --extra all || pip install -e ".[all]"

setup-hooks:       ## Install pre-commit git hooks
	pre-commit install

##@ Quality
lint:              ## ruff + black --check
	$(PY) -m emerald_ai lint

format:            ## ruff --fix + black
	$(PY) -m emerald_ai format

typecheck:         ## mypy strict
	$(PY) -m emerald_ai typecheck

test:              ## pytest with coverage
	$(PY) -m emerald_ai test

test-fast:         ## skip slow + integration tests
	$(PY) -m emerald_ai test --fast

test-cov:          ## pytest + open HTML coverage report
	$(PY) -m emerald_ai test --cov

check:             ## lint + typecheck + test
	$(PY) -m emerald_ai check

##@ Pipeline (stubs until ML implementation lands)
eda:               ## Run exploratory data analysis (proposal §5.4)
	$(PY) -m emerald_ai eda

preprocess:        ## Build preprocessing pipeline (proposal §5.3, §5.5, §5.7)
	$(PY) -m emerald_ai preprocess

train:             ## Train all model families (proposal §5.8, §5.9)
	$(PY) -m emerald_ai train --model all

evaluate:          ## Compute metrics + calibration (proposal §5.10, §5.13)
	$(PY) -m emerald_ai evaluate

explain:           ## SHAP + counterfactual + fidelity (proposal §5.11)
	$(PY) -m emerald_ai explain

audit:             ## Fairness + robustness + drift (proposal §5.12)
	$(PY) -m emerald_ai audit --axis all

reproduce: preprocess train evaluate explain audit  ## End-to-end pipeline (≤8h target)

##@ Authoring
proposal:          ## Rebuild docs/proposal/proposal_second_draft.docx
	$(PY) -m emerald_ai proposal

literature:        ## Regenerate research/literature/papers/*.md from build_papers.py
	$(PY) -m emerald_ai literature

##@ Research automation
research:          ## Run a research-engine sweep
	$(PY) -m emerald_ai research run

research-force:    ## Re-process every paper
	$(PY) -m emerald_ai research run --force

research-status:   ## Show current brain state
	$(PY) -m emerald_ai research status

research-graph:    ## Emit citation graph as Graphviz DOT
	$(PY) -m emerald_ai research graph

##@ Application
api:               ## Start FastAPI dev server (reload on change)
	$(PY) -m emerald_ai api

web:               ## Run React dev server (when scaffold exists)
	cd apps/web && pnpm dev

docker-up:         ## Start full stack via docker-compose
	docker compose up --build

docker-down:       ## Stop full stack
	docker compose down

##@ Housekeeping
clean:             ## Remove caches + build artefacts (keeps data/ and .venv/)
	$(PY) -m emerald_ai clean

clean-all:         ## Also remove .venv/ and web/node_modules/
	$(PY) -m emerald_ai clean --all
