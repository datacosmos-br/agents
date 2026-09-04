# Development support and gate composition for the optionless agentsctl runtime.

AGENTSCTL := uv run agentsctl
PYTEST_SCRATCH := $(CURDIR)/.test-tmp
WHEEL_SMOKE := $(PYTEST_SCRATCH)/wheel-smoke
WHEEL_PROJECT := $(PYTEST_SCRATCH)/wheel-project
override export UV_PROJECT_ENVIRONMENT := $(CURDIR)/.venv
override export VIRTUAL_ENV := $(CURDIR)/.venv

.DEFAULT_GOAL := help
.PHONY: help setup docs audit check waza static fmt fix shell duplication build test spec coverage providers projection gen ci security temp validate-live validate-wheel clean
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

## environment provisioning
setup: ## create the repository-local runtime environment
	$(call BANNER,setup · uv venv + sync)
	@uv venv --clear
	@uv sync --all-groups

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

waza: ## enforce Waza token ceilings across skills, rules, and commands
	$(call BANNER,waza · token ceilings)
	@waza tokens check $(CURDIR)/skills --strict --no-update-check
	@waza tokens check $(CURDIR)/rules --strict --no-update-check
	@waza tokens check $(CURDIR)/commands --strict --no-update-check

static: ## lint, formatting, and Python type analysis
	$(call BANNER,static · ruff + pyright + mypy)
	@uv run ruff check src tests
	@uv run ruff format --check src tests
	@uv run pyright src tests
	@uv run mypy src tests

fmt: ## apply canonical Python formatting during development
	$(call BANNER,fmt · ruff format)
	@uv run ruff format src tests

fix: ## apply canonical Python lint corrections during development
	$(call BANNER,fix · ruff check --fix)
	@uv run ruff check --fix src tests

shell: ## validate shell scripts and GitHub workflows
	$(call BANNER,shell · actionlint)
	@actionlint .github/workflows/*.yml

duplication: ## enforce zero strict duplication in canonical Python source
	$(call BANNER,duplication · jscpd)
	@jscpd src tests --config $(CURDIR)/.jscpd.json --exit-code 1

build: ## build source and wheel artifacts
	$(call BANNER,build · sdist + wheel)
	@find config skills rules commands agents workflows docs -name __pycache__ -type d -exec rm -rf {} +
	@uv build

test: ## execute the complete Python test suite
	$(call BANNER,test · pytest)
	$(call RUN_PYTEST,$(FILE) $(FILES) $(if $(MATCH),-k '$(MATCH)') $(PYTEST_ARGS))

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

gen: projection ## converge every canonical projection (generation surface)

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

validate-wheel: ## validate one published agents-governance wheel in isolation
	$(call BANNER,validate-wheel · published package)
	@test -n "$(WHEEL)" || { echo 'WHEEL=<path> is required' >&2; exit 2; }
	@test -f "$(WHEEL)" || { echo "wheel does not exist: $(WHEEL)" >&2; exit 2; }
	@uv venv --clear $(WHEEL_SMOKE)
	@uv pip install --python $(WHEEL_SMOKE)/bin/python $(WHEEL)
	@$(WHEEL_SMOKE)/bin/agentsctl doctor
	@mkdir -p $(WHEEL_PROJECT)/.git $(WHEEL_PROJECT)/.agents
	@printf '%s\n' '{"version":1,"agents":[],"opt_ins":[],"selected_tags":[]}' > $(WHEEL_PROJECT)/.agents/projection.json
	@env -C $(WHEEL_PROJECT) HOME=$(WHEEL_PROJECT) $(WHEEL_SMOKE)/bin/agentsctl check
