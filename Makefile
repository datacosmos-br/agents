# Development support and gate composition for the optionless agentsctl runtime.

AGENTSCTL := uv run agentsctl
PYTEST_SCRATCH := $(CURDIR)/.test-tmp

.DEFAULT_GOAL := help
.PHONY: help docs audit check static fmt shell build test spec coverage providers projection ci security temp validate-live clean
.DELETE_ON_ERROR:

define BANNER
	@if [ -z "$$NO_COLOR" ]; then printf '\033[1;36m▶\033[0m %s\n' "$(1)"; else printf '▶ %s\n' "$(1)"; fi
endef

define RUN_PYTEST
	@mkdir -p $(PYTEST_SCRATCH)/pytest.$$PPID
	@uv run pytest --basetemp $(PYTEST_SCRATCH)/pytest.$$PPID $(1)
	@rmdir $(PYTEST_SCRATCH)/pytest.$$PPID
endef

help: ## show the complete development surface
	@awk 'BEGIN{FS=":.*## "} /^## /{sub(/^## */,""); print ""; print} /^[a-z][a-z_-]*:.*## /{printf "  %-14s %s\n",$$1,$$2}' $(MAKEFILE_LIST)

## read-only development gates
docs: ## validate documentation delivery contracts
	$(call BANNER,docs · delivery contracts)
	$(call RUN_PYTEST,tests/test_delivery_contracts.py)

audit: ## inspect the complete canonical runtime inventory
	$(call BANNER,audit · agentsctl doctor)
	@$(AGENTSCTL) doctor

check: ## execute the complete offline governance validation
	$(call BANNER,check · agentsctl check)
	@$(AGENTSCTL) check

static: ## lint, formatting, and Python type analysis
	$(call BANNER,static · ruff + pyright + mypy)
	@uv run ruff check src tests
	@uv run ruff format --check src tests
	@uv run pyright src tests
	@uv run mypy src tests

fmt: ## apply canonical Python formatting during development
	$(call BANNER,fmt · ruff)
	@uv run ruff check --fix src tests
	@uv run ruff format src tests

shell: ## validate shell scripts and GitHub workflows
	$(call BANNER,shell · actionlint)
	@actionlint .github/workflows/*.yml

build: ## build source and wheel artifacts
	$(call BANNER,build · sdist + wheel)
	@uv build

test: ## execute the complete Python test suite
	$(call BANNER,test · pytest)
	$(call RUN_PYTEST,$(PYTEST_ARGS))

spec: ## validate every canonical evaluation specification
	$(call BANNER,spec · agentsctl evaluate)
	@$(AGENTSCTL) evaluate

coverage: spec ## require complete evaluation coverage

providers: audit ## validate every declared provider contract

temp: check ## validate storage and temporary-filesystem governance

## mutating and live gates
projection: ## converge every canonical projection
	$(call BANNER,projection · agentsctl sync)
	@$(AGENTSCTL) sync

security: ## execute every configured security scanner
	$(call BANNER,security · agentsctl secure)
	@$(AGENTSCTL) secure

validate-live: ## execute the exact live model workflow
	$(call BANNER,validate-live · agentsctl live)
	@$(AGENTSCTL) live

clean: ## remove only validated generated artifacts
	$(call BANNER,clean · agentsctl clean)
	@$(AGENTSCTL) clean

## complete offline composition
ci: docs audit check static shell build test coverage providers temp ## run every offline development gate
