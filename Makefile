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
override export GIT_CEILING_DIRECTORIES := $(abspath $(CURDIR)/..)
override export MISE_CEILING_PATHS := $(abspath $(CURDIR)/..)
override export MISE_GLOBAL_CONFIG_FILE := $(CURDIR)/config/mise-isolation.toml
override export MISE_SYSTEM_CONFIG_FILE := $(CURDIR)/config/mise-isolation.toml
override export MISE_OVERRIDE_CONFIG_FILENAMES := .mise.toml
override export MISE_OVERRIDE_TOOL_VERSIONS_FILENAMES := none
unexport UV_PYTHON

.DEFAULT_GOAL := help
.PHONY: help setup upg gen docs audit check runtime waza crg-check static conform fmt fix mod mod-check shell duplication build test test-full ci validate-artifacts publish
.DELETE_ON_ERROR:

define BANNER
	@if [ -z "$$NO_COLOR" ]; then printf '\033[1;36m▶\033[0m %s\n' "$(1)"; else printf '▶ %s\n' "$(1)"; fi
endef

define RUN_TESTMON
	@TESTMON_MODE=$(1) uv run python tools/testmon_gate.py
endef

help: ## show the complete selector-free development surface
	@awk 'BEGIN{FS=":.*## "} /^## /{sub(/^## */,""); print ""; print} /^[a-z][a-z_-]*:.*## /{printf "  %-14s %s\n",$$1,$$2}' $(MAKEFILE_LIST)

## environment provisioning
setup: ## create the declared repository runtime environment
	$(call BANNER,setup · locked mise install + uv venv + locked sync)
	@mise install --yes
	@$(MISE_EXEC) uv venv --python python --clear
	@$(MISE_EXEC) uv sync --all-groups --locked

upg: ## resolve newest declared tools and dependencies into committed locks
	$(call BANNER,upg · mise lock + uv lock)
	@mise lock --bump
	@MISE_LOCKED=false $(MISE_EXEC) uv lock --upgrade --refresh
	@MISE_LOCKED=false $(MISE_EXEC) uv sync --all-groups --locked

## generation + mutation
gen: ## project the governance capsule into provider hooks and instruction files
	$(call BANNER,gen · governance capsule + provider projections)
	@uv run python tools/sync_governance.py

## development gates
check: ## run package non-test gates; host CRG acceptance uses make crg-check
	$(call BANNER,check · complete non-test gate composition)
	@$(MAKE) docs
	@$(MAKE) static
	@$(MAKE) mod-check
	@$(MAKE) conform
	@$(MAKE) waza
	@$(MAKE) runtime

docs: ## validate documentation through the public bundle contract
	@$(MAKE) audit
	@uv run python tools/check_docs_links.py

audit: ## print the complete public semantic inventory
	$(call BANNER,audit · GovernanceBundle.load)
	@if [ -e "$(TESTMON_DATAFILE)" ]; then \
		test "$$(sqlite3 "$(TESTMON_DATAFILE)" 'PRAGMA quick_check;')" = ok; \
	fi
	@uv run python -c 'from agents_governance import GovernanceBundle; bundle = GovernanceBundle.load(); d = bundle.delivery; print(f"{len(bundle.skills)} skills, {len(bundle.commands)} commands, {len(bundle.agents)} agents, {len(bundle.rules)} rules"); print(f"capsule {d.total_chars} chars (prelude {d.prelude_chars} + rules {d.rule_summary_chars} + skills {d.skill_index_chars}), headroom {d.headroom_chars}/{d.contract.capsule_budget_chars - d.contract.restore_list_reserve_chars}")'

waza: ## validate provider-neutral skill suites with Waza
	@$(MAKE) audit
	$(call BANNER,waza · provider-neutral suites + deterministic spec proof)
	@uv run python tools/waza_gate.py

crg-check: ## verify CRG policy convergence across governed workspaces (ai-hub sync-crg-workspaces --check)
	$(call BANNER,crg-check · CRG policy drift gate (ag-nq7q))
	@ai-hub sync-crg-workspaces --check
	@printf '%s\n' 'CRG workspace policies and watch configuration verified.'

static: ## lint, formatting, and Python type analysis
	$(call BANNER,static · ruff + pyright + mypy)
	@uv run ruff check src tests tools
	@uv run ruff format --check src tests tools
	@uv run pyright src tests tools
	@uv run mypy src tests tools
	@PYTHON_RESOURCES_OPERATION=check uv run python tools/python_resources_gate.py

conform: ## validate workflow and zero-duplication conformance
	@$(MAKE) shell
	@$(MAKE) duplication
	@git diff --check

fmt: ## apply canonical Python formatting
	$(call BANNER,fmt · ruff format)
	@uv run ruff format src tests tools
	@PYTHON_RESOURCES_OPERATION=format uv run python tools/python_resources_gate.py

fix: ## apply canonical corrections
	$(call BANNER,fix · ruff)
	@uv run ruff check --fix src tests tools
	@PYTHON_RESOURCES_OPERATION=fix uv run python tools/python_resources_gate.py
	@TESTMON_MODE=repair uv run python tools/testmon_gate.py

mod-check: ## test ast-grep rules and reject structural migration residue
	$(call BANNER,mod-check · ast-grep tests + strict structural scan)
	@$(MISE_EXEC) ast-grep test --config "$(CURDIR)/sgconfig.yml"
	@$(MISE_EXEC) ast-grep scan --config "$(CURDIR)/sgconfig.yml" --error "$(CURDIR)/evals"
	@EVAL_YAML_MODE=check uv run python tools/normalize_eval_yaml.py

mod: ## apply tested structural migrations
	$(call BANNER,mod · ast-grep structural rewrite)
	@$(MISE_EXEC) ast-grep test --config "$(CURDIR)/sgconfig.yml" --update-all
	@$(MISE_EXEC) ast-grep scan --config "$(CURDIR)/sgconfig.yml" --update-all "$(CURDIR)/evals"
	@uv run python tools/normalize_eval_yaml.py
	@$(MAKE) mod-check
	@$(MAKE) audit

shell: ## validate shell scripts and GitHub workflows
	$(call BANNER,shell · actionlint + shellcheck)
	@$(MISE_EXEC) actionlint .github/workflows/*.yml
	@$(MISE_EXEC) shellcheck skills/tool/beads-organization/scripts/reconcile-inventory.sh

duplication: ## enforce zero strict duplication in canonical source and evaluations
	$(call BANNER,duplication · jscpd)
	@$(MISE_EXEC) jscpd src tests tools evals --config $(CURDIR)/.jscpd.json --exit-code 1

build: ## build source and wheel artifacts
	$(call BANNER,build · sdist + wheel)
	@ARTIFACT_MODE=build uv run python tools/artifact_gate.py

validate-artifacts: ## validate the exact sdist and wheel in isolation
	$(call BANNER,validate-artifacts · installed public bundle from sdist + wheel)
	@ARTIFACT_MODE=validate uv run python tools/artifact_gate.py

runtime: ## build, install, and load the public wheel
	$(call BANNER,runtime · atomic build + isolated sdist/wheel proof)
	@ARTIFACT_MODE=runtime uv run python tools/artifact_gate.py

test: ## run affected tests through the shared testmon cache
	$(call BANNER,test · pytest-testmon affected selection)
	$(call RUN_TESTMON,incremental)

test-full: ## run incremental then all tests through the same cache
	@$(MAKE) test
	$(call BANNER,test-full · pytest-testmon no-selection)
	$(call RUN_TESTMON,full)

## complete offline composition
ci: ## run package gates and cached tests; host CRG acceptance uses make crg-check
	@$(MAKE) check
	@$(MAKE) test-full

## release publication
publish: ## publish the validated tag artifacts
	$(call BANNER,publish · immutable GitHub release)
	@ARTIFACT_MODE=publish uv run python tools/artifact_gate.py
