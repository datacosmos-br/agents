# Public development surface for the immutable semantic governance bundle.

MISE_EXEC := mise exec --
CACHE_HOME := $(if $(XDG_CACHE_HOME),$(XDG_CACHE_HOME),$(HOME)/.cache)
PYRIGHT_CACHE_ROOT := $(CACHE_HOME)/agents-governance/pyright
TEST_STATE_ROOT := $(CACHE_HOME)/agents-governance/pytest
TESTMON_DATAFILE := $(TEST_STATE_ROOT)/.testmondata
ARTIFACT_STATE_ROOT := $(CACHE_HOME)/agents-governance/artifacts
WAZA_STATE_ROOT := $(CACHE_HOME)/agents-governance/waza
override export TESTMON_DATAFILE := $(TESTMON_DATAFILE)
override export COVERAGE_CORE := ctrace
override export ARTIFACT_STATE_ROOT := $(ARTIFACT_STATE_ROOT)
override export PYRIGHT_PYTHON_CACHE_DIR := $(PYRIGHT_CACHE_ROOT)
override export WAZA_STATE_ROOT := $(WAZA_STATE_ROOT)
override export UV_PROJECT_ENVIRONMENT := $(CURDIR)/.venv
override export VIRTUAL_ENV := $(CURDIR)/.venv

.DEFAULT_GOAL := help
.PHONY: help setup gen docs propagate audit check runtime waza static conform fmt fix mod mod-check shell duplication build test test-full ci validate-artifacts publish
.DELETE_ON_ERROR:

define BANNER
	@if [ -z "$$NO_COLOR" ]; then printf '\033[1;36m▶\033[0m %s\n' "$(1)"; else printf '▶ %s\n' "$(1)"; fi
endef

define REQUIRE_APPLY
	@test "$(APPLY)" = Y || { echo 'APPLY=Y is required for this operation' >&2; exit 2; }
endef

define REJECT_APPLY
	@test -z "$(APPLY)" || { echo 'APPLY is not accepted for this read-only operation' >&2; exit 2; }
endef

define RUN_TESTMON
	@TESTMON_MODE=$(1) uv run python tools/testmon_gate.py
endef

help: ## show the complete selector-free development surface
	$(call REJECT_APPLY)
	@awk 'BEGIN{FS=":.*## "} /^## /{sub(/^## */,""); print ""; print} /^[a-z][a-z_-]*:.*## /{printf "  %-14s %s\n",$$1,$$2}' $(MAKEFILE_LIST)

## environment provisioning
setup: ## create the declared repository runtime environment; requires APPLY=Y
	$(call REQUIRE_APPLY)
	$(call BANNER,setup · mise install + uv venv + sync)
	@mise install
	@uv venv --clear
	@uv sync --all-groups

## development gates
check: ## run every applicable non-test gate; requires APPLY=Y
	$(call REQUIRE_APPLY)
	$(call BANNER,check · complete non-test gate composition)
	@$(MAKE) docs APPLY=Y
	@$(MAKE) propagate APPLY=Y
	@$(MAKE) static APPLY=Y
	@$(MAKE) mod-check APPLY=Y
	@$(MAKE) conform APPLY=Y
	@$(MAKE) waza APPLY=Y
	@$(MAKE) runtime APPLY=Y

docs: ## validate documentation through the public bundle contract; requires APPLY=Y
	$(call REQUIRE_APPLY)
	@$(MAKE) audit APPLY=Y
	@uv run python tools/check_docs_links.py

propagate: ## regenerate AI Hub project configuration; requires APPLY=Y
	$(call REQUIRE_APPLY)
	$(call BANNER,propagate · project surface configuration)
	@uv run python tools/render_project_projection.py

audit: ## print the complete public semantic inventory; requires APPLY=Y
	$(call REQUIRE_APPLY)
	$(call BANNER,audit · GovernanceBundle.load)
	@if [ -e "$(TESTMON_DATAFILE)" ]; then \
		test "$$(sqlite3 "$(TESTMON_DATAFILE)" 'PRAGMA quick_check;')" = ok; \
	fi
	@uv run python -c 'from agents_governance import GovernanceBundle; bundle = GovernanceBundle.load(); print(f"{len(bundle.skills)} skills, {len(bundle.commands)} commands, {len(bundle.agents)} agents, {len(bundle.rules)} rules")'

waza: ## validate provider-neutral skill suites with Waza; requires APPLY=Y
	$(call REQUIRE_APPLY)
	@$(MAKE) audit APPLY=Y
	$(call BANNER,waza · provider-neutral suites + deterministic spec proof)
	@uv run python tools/waza_gate.py

static: ## lint, formatting, and Python type analysis; requires APPLY=Y
	$(call REQUIRE_APPLY)
	$(call BANNER,static · ruff + pyright + mypy)
	@uv run ruff check src tests tools
	@uv run ruff format --check src tests tools
	@uv run pyright src tests tools
	@uv run mypy src tests tools

conform: ## validate workflow and zero-duplication conformance; requires APPLY=Y
	$(call REQUIRE_APPLY)
	@$(MAKE) shell
	@$(MAKE) duplication
	@git diff --check

fmt: ## apply canonical Python formatting; requires APPLY=Y
	$(call REQUIRE_APPLY)
	$(call BANNER,fmt · ruff format)
	@uv run ruff format src tests tools

fix: ## apply canonical corrections; requires APPLY=Y
	$(call REQUIRE_APPLY)
	$(call BANNER,fix · ruff)
	@uv run ruff check --fix src tests tools
	@TESTMON_MODE=repair uv run python tools/testmon_gate.py

mod-check: ## test ast-grep rules and reject structural migration residue; requires APPLY=Y
	$(call REQUIRE_APPLY)
	$(call BANNER,mod-check · ast-grep tests + strict structural scan)
	@$(MISE_EXEC) ast-grep test --config "$(CURDIR)/sgconfig.yml"
	@$(MISE_EXEC) ast-grep scan --config "$(CURDIR)/sgconfig.yml" --error "$(CURDIR)/evals"

mod: ## apply tested structural migrations; requires APPLY=Y
	$(call REQUIRE_APPLY)
	$(call BANNER,mod · ast-grep structural rewrite)
	@$(MISE_EXEC) ast-grep test --config "$(CURDIR)/sgconfig.yml" --update-all
	@$(MISE_EXEC) ast-grep scan --config "$(CURDIR)/sgconfig.yml" --update-all "$(CURDIR)/evals"
	@uv run python tools/normalize_eval_yaml.py
	@$(MAKE) mod-check APPLY=Y
	@$(MAKE) audit APPLY=Y

shell: ## validate shell scripts and GitHub workflows; requires APPLY=Y
	$(call REQUIRE_APPLY)
	$(call BANNER,shell · actionlint + shellcheck)
	@$(MISE_EXEC) actionlint .github/workflows/*.yml
	@$(MISE_EXEC) shellcheck skills/tool/beads-organization/scripts/reconcile-inventory.sh

duplication: ## enforce zero strict duplication in canonical source and evaluations; requires APPLY=Y
	$(call REQUIRE_APPLY)
	$(call BANNER,duplication · jscpd)
	@$(MISE_EXEC) jscpd src tests tools evals --config $(CURDIR)/.jscpd.json --exit-code 1

gen: ## generate governance projections from canonical owners; requires APPLY=Y
	$(call REQUIRE_APPLY)
	$(call BANNER,gen · canonical projections)
	@uv run python tools/render_project_projection.py

build: ## build source and wheel artifacts; requires APPLY=Y
	$(call REQUIRE_APPLY)
	$(call BANNER,build · sdist + wheel)
	@ARTIFACT_MODE=build uv run python tools/artifact_gate.py

validate-artifacts: ## validate the exact sdist and wheel in isolation; requires APPLY=Y
	$(call REQUIRE_APPLY)
	$(call BANNER,validate-artifacts · installed public bundle from sdist + wheel)
	@ARTIFACT_MODE=validate uv run python tools/artifact_gate.py

runtime: ## build, install, and load the public wheel; requires APPLY=Y
	$(call REQUIRE_APPLY)
	$(call BANNER,runtime · atomic build + isolated sdist/wheel proof)
	@ARTIFACT_MODE=runtime uv run python tools/artifact_gate.py

test: ## run affected tests through the shared testmon cache; requires APPLY=Y
	$(call REQUIRE_APPLY)
	$(call BANNER,test · pytest-testmon affected selection)
	$(call RUN_TESTMON,incremental)

test-full: ## run incremental then all tests through the same cache; requires APPLY=Y
	$(call REQUIRE_APPLY)
	@$(MAKE) test APPLY=Y
	$(call BANNER,test-full · pytest-testmon no-selection)
	$(call RUN_TESTMON,full)

## complete offline composition
ci: ## run every gate in runtime-first order; requires APPLY=Y
	$(call REQUIRE_APPLY)
	@$(MAKE) check APPLY=Y
	@$(MAKE) test-full APPLY=Y

## release publication
publish: ## publish the validated tag artifacts; requires APPLY=Y
	$(call REQUIRE_APPLY)
	$(call BANNER,publish · immutable GitHub release)
	@ARTIFACT_MODE=publish uv run python tools/artifact_gate.py
