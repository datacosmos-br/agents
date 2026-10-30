# Public development surface for the immutable semantic governance bundle.

MISE_EXEC := mise exec --
UV_RUN := $(MISE_EXEC) uv run --no-sync
CACHE_HOME := $(if $(XDG_CACHE_HOME),$(XDG_CACHE_HOME),$(HOME)/.cache)
PYRIGHT_CACHE_ROOT := $(CACHE_HOME)/agents-governance/pyright
ARTIFACT_STATE_ROOT := $(CACHE_HOME)/agents-governance/artifacts
WAZA_STATE_ROOT := $(CACHE_HOME)/agents-governance/waza
override export COVERAGE_CORE := ctrace
override export ARTIFACT_STATE_ROOT := $(ARTIFACT_STATE_ROOT)
# Opt-in artifact-runtime instrumentation; it never selects an operation or scope.
export ARTIFACT_PROFILE
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
unexport UV_PYTHON UV_PROJECT

.DEFAULT_GOAL := help
PUBLIC_VERBS := help setup upg gen docs audit check runtime waza crg-check lint static conform fmt fix mod mod-check shell duplication build test test-full ci validate-artifacts publish profile-mypy-resources profile-mypy-resources-report profile-waza profile-waza-report
.PHONY: $(PUBLIC_VERBS)
.DELETE_ON_ERROR:

ifeq ($(MAKELEVEL),0)
$(PUBLIC_VERBS): _bounded
.PHONY: _bounded
_bounded:
	+@timeout --signal=TERM --kill-after=2s 118s $(MAKE) --no-print-directory $(or $(MAKECMDGOALS),help)
else

define BANNER
	@if [ -z "$$NO_COLOR" ]; then printf '\033[1;36m▶\033[0m %s\n' "$(1)"; else printf '▶ %s\n' "$(1)"; fi
	@if [ "$$ARTIFACT_PROFILE" = "1" ]; then printf 'COMMAND stage %s utc=' "$(1)"; date -u '+%Y-%m-%dT%H:%M:%SZ'; fi
endef

define RUN_TESTMON
	@TESTMON_MODE=$(1) $(UV_RUN) python tools/testmon_gate.py
endef

help: ## show the complete selector-free development surface
	@awk 'BEGIN{FS=":.*## "} /^## /{sub(/^## */,""); print ""; print} /^[a-z][a-z_-]*:.*## /{printf "  %-14s %s\n",$$1,$$2}' $(MAKEFILE_LIST)

## environment provisioning
setup: ## create the declared repository runtime environment
	$(call BANNER,setup · locked mise install + uv venv + locked sync)
	@MISE_LOCKED=true mise install --yes
	@MISE_LOCKED=true $(MISE_EXEC) uv venv --python python --clear
	@MISE_LOCKED=true $(MISE_EXEC) uv sync --all-groups --locked

upg: ## resolve newest declared tools and dependencies into committed locks
	$(call BANNER,upg · mise lock + uv lock)
	@MISE_LOCKED=false mise lock --upgrade --bump
	@MISE_LOCKED=false $(MISE_EXEC) uv lock --upgrade --refresh

## generation + mutation
gen: ## project Beads activation and governance provider outputs
	$(call BANNER,gen · Beads activation + governance projections)
	@$(UV_RUN) python tools/sync_beads_activation.py
	@$(UV_RUN) python tools/sync_governance.py

## development gates
check: ## run package non-test gates; host CRG acceptance uses make crg-check
	$(call BANNER,check · complete non-test gate composition)
	+@$(MAKE) --jobs=2 runtime docs static mod-check conform waza

docs: ## validate documentation through the public bundle contract
	@$(MAKE) audit
	@$(UV_RUN) python tools/check_docs_links.py

audit: ## print the complete public semantic inventory
	$(call BANNER,audit · GovernanceBundle.load)
	@$(UV_RUN) python -c 'from agents_governance import GovernanceBundle, catalog_resources; bundle = GovernanceBundle.load(); resources = catalog_resources(bundle); d = bundle.delivery; print(f"{len(bundle.skills)} skills, {len(bundle.commands)} commands, {len(bundle.agents)} agents, {len(bundle.rules)} rules"); print(f"{len(resources)} authenticated neutral catalog resources"); print(f"capsule {d.total_chars} chars (prelude {d.prelude_chars} + rules {d.rule_summary_chars} + skills {d.skill_index_chars}), headroom {d.headroom_chars}/{d.contract.capsule_budget_chars - d.contract.restore_list_reserve_chars}")'

waza: ## validate provider-neutral skill suites with Waza
	$(call BANNER,waza · provider-neutral suites + deterministic spec proof)
	@$(UV_RUN) python tools/waza_gate.py

crg-check: ## verify CRG policy convergence across governed workspaces (ai-hub sync-crg-workspaces --check)
	$(call BANNER,crg-check · CRG policy drift gate (ag-nq7q))
	@ai-hub sync-crg-workspaces --check
	@printf '%s\n' 'CRG workspace policies and watch configuration verified.'

lint: ## fast external lint and formatting check
	$(call BANNER,lint · ruff check + ruff format --check)
	@$(UV_RUN) ruff check src tests tools
	@$(UV_RUN) ruff format --check src tests tools

static: ## lint, formatting, and whole-program Python type analysis (local only)
	@$(MAKE) lint
	$(call BANNER,static · pyright + mypy)
	@PYTHON_RESOURCES_OPERATION=check $(UV_RUN) python tools/python_resources_gate.py

profile-mypy-resources: ## profile native Mypy over every declared Python skill resource
	@mkdir -p .reports/profiles
	@PYTHON_RESOURCES_OPERATION=profile-mypy $(UV_RUN) python tools/python_resources_gate.py

profile-mypy-resources-report: ## read the native Mypy resource profile
	@$(UV_RUN) python -c 'import pstats; pstats.Stats(".reports/profiles/mypy-resources.pstats").sort_stats("cumtime").print_stats(30)'

profile-waza: ## profile the Waza coordinator; child code is not instrumented
	@mkdir -p .reports/profiles
	@$(UV_RUN) python -m cProfile -o .reports/profiles/waza.pstats tools/waza_gate.py

profile-waza-report: ## read coordinator costs and child waits, not child call profiles
	$(call BANNER,profile-waza-report · parent Python only; child work appears as waits)
	@$(UV_RUN) python -c 'import pstats; pstats.Stats(".reports/profiles/waza.pstats").sort_stats("cumtime").print_stats(30)'

conform: ## validate workflow and zero-duplication conformance
	@$(MAKE) shell
	@$(MAKE) duplication
	@git diff --check

fmt: ## apply canonical Python formatting
	$(call BANNER,fmt · ruff format)
	@$(UV_RUN) ruff format src tests tools
	@PYTHON_RESOURCES_OPERATION=format $(UV_RUN) python tools/python_resources_gate.py

fix: ## apply canonical corrections
	$(call BANNER,fix · ruff)
	@$(UV_RUN) ruff check --fix src tests tools
	@PYTHON_RESOURCES_OPERATION=fix $(UV_RUN) python tools/python_resources_gate.py
	@TESTMON_MODE=repair $(UV_RUN) python tools/testmon_gate.py

mod-check: ## test ast-grep rules and reject structural migration residue
	$(call BANNER,mod-check · ast-grep tests + strict structural scan)
	@$(MISE_EXEC) ast-grep test --config "$(CURDIR)/sgconfig.yml"
	@$(MISE_EXEC) ast-grep scan --config "$(CURDIR)/sgconfig.yml" --error "$(CURDIR)/evals"
	@EVAL_YAML_MODE=check $(UV_RUN) python tools/normalize_eval_yaml.py

mod: ## apply tested structural migrations
	$(call BANNER,mod · ast-grep structural rewrite)
	@$(MISE_EXEC) ast-grep test --config "$(CURDIR)/sgconfig.yml" --update-all
	@$(MISE_EXEC) ast-grep scan --config "$(CURDIR)/sgconfig.yml" --update-all "$(CURDIR)/evals"
	@$(UV_RUN) python tools/normalize_eval_yaml.py
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
	@ARTIFACT_MODE=build $(UV_RUN) python tools/artifact_gate.py

validate-artifacts: ## validate the exact sdist and wheel in isolation
	$(call BANNER,validate-artifacts · installed public bundle from sdist + wheel)
	@ARTIFACT_MODE=validate $(UV_RUN) python tools/artifact_gate.py

runtime: ## build, install, and load the public wheel
	$(call BANNER,runtime · atomic build + isolated sdist/wheel proof)
	@ARTIFACT_MODE=runtime $(UV_RUN) python tools/artifact_gate.py

test: ## run affected tests through the testmon database at its tool default
	$(call BANNER,test · pytest-testmon affected selection)
	$(call RUN_TESTMON,incremental)

test-full: ## run the complete local suite without the testmon plugin or database
	$(call BANNER,test-full · pytest without testmon)
	$(call RUN_TESTMON,full)

## CI composition: fast external gates and make test only
ci: ## run the fast external gates and make test; check and test-full stay local
	@$(MAKE) lint
	@$(MAKE) shell
	@$(MAKE) duplication
	@$(MAKE) test

## release publication
publish: ## publish the validated tag artifacts
	$(call BANNER,publish · immutable GitHub release)
	@ARTIFACT_MODE=publish $(UV_RUN) python tools/artifact_gate.py

endif
