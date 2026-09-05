# Public development surface for the immutable semantic governance bundle.

MISE_EXEC := mise exec --
CACHE_HOME := $(if $(XDG_CACHE_HOME),$(XDG_CACHE_HOME),$(HOME)/.cache)
PYRIGHT_CACHE_ROOT := $(CACHE_HOME)/agents-governance/pyright
TEST_STATE_ROOT := $(CACHE_HOME)/agents-governance/pytest
TESTMON_DATAFILE := $(TEST_STATE_ROOT)/.testmondata
PYTEST_SCRATCH := $(TEST_STATE_ROOT)/scratch
WHEEL_SMOKE := $(CACHE_HOME)/agents-governance/wheel-smoke
WAZA_PROJECTION_ROOT := $(CACHE_HOME)/agents-governance/waza-projection
OBSOLETE_LOCAL_PATHS := \
	$(CURDIR)/.testmondata \
	$(CURDIR)/.pytest-scratch \
	$(CURDIR)/.pytest_cache \
	$(CURDIR)/.test-tmp \
	$(CURDIR)/.reports \
	$(CURDIR)/.waza-cache \
	$(CURDIR)/results \
	$(CURDIR)/src/agents_governance/__pycache__ \
	$(CURDIR)/tests/__pycache__
override export TESTMON_DATAFILE := $(TESTMON_DATAFILE)
override export PYTHONDONTWRITEBYTECODE := 1
override export PYRIGHT_PYTHON_CACHE_DIR := $(PYRIGHT_CACHE_ROOT)
override export WAZA_PROJECTION_ROOT := $(WAZA_PROJECTION_ROOT)
override export UV_PROJECT_ENVIRONMENT := $(CURDIR)/.venv
override export VIRTUAL_ENV := $(CURDIR)/.venv

.DEFAULT_GOAL := help
.PHONY: help setup docs audit check runtime waza static conform fmt fix mod mod-check shell duplication build test test-full ci validate-wheel publish
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
	@install -d -m 700 "$(TEST_STATE_ROOT)" "$(PYTEST_SCRATCH)"
	@uv run pytest --basetemp "$(PYTEST_SCRATCH)" --testmon $(1)
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
	@$(MAKE) static APPLY=Y
	@$(MAKE) mod-check APPLY=Y
	@$(MAKE) conform APPLY=Y
	@$(MAKE) waza APPLY=Y
	@$(MAKE) runtime APPLY=Y

docs: ## validate documentation through the public bundle contract; requires APPLY=Y
	$(call REQUIRE_APPLY)
	@$(MAKE) audit APPLY=Y

audit: ## print the complete public semantic inventory; requires APPLY=Y
	$(call REQUIRE_APPLY)
	$(call BANNER,audit · GovernanceBundle.load)
	@for obsolete in $(OBSOLETE_LOCAL_PATHS); do \
		test ! -e "$$obsolete" || { echo "obsolete local cache: $$obsolete" >&2; exit 1; }; \
	done
	@if [ -e "$(TESTMON_DATAFILE)" ]; then \
		test "$$(sqlite3 "$(TESTMON_DATAFILE)" 'PRAGMA quick_check;')" = ok; \
	fi
	@uv run python -c 'from agents_governance import GovernanceBundle; bundle = GovernanceBundle.load(); print(f"{len(bundle.skills)} skills, {len(bundle.commands)} commands, {len(bundle.agents)} agents, {len(bundle.rules)} rules")'

waza: ## validate provider-neutral skill suites with Waza; requires APPLY=Y
	$(call REQUIRE_APPLY)
	@$(MAKE) audit APPLY=Y
	$(call BANNER,waza · provider-neutral suites + deterministic spec proof)
	@test "$$($(MISE_EXEC) waza --version)" = 'waza version 0.38.7'
	@uv run python tools/render_waza_projection.py
	@env -C "$(WAZA_PROJECTION_ROOT)" $(MISE_EXEC) waza tokens check ./skills --strict --no-update-check
	@$(MISE_EXEC) waza tokens check "$(CURDIR)/rules" --strict --no-update-check
	@$(MISE_EXEC) waza tokens check "$(CURDIR)/commands" --strict --no-update-check
	@expected="$$(find "$(WAZA_PROJECTION_ROOT)/evals" -mindepth 2 -maxdepth 2 -type f -name eval.yaml | wc -l)"; \
	test "$$expected" -gt 0 || { echo 'Waza projection contains no evaluation suites' >&2; exit 1; }; \
	verified=0; \
	for evaluation in "$(WAZA_PROJECTION_ROOT)"/evals/*/eval.yaml; do \
		test -f "$$evaluation" || { echo "missing projected evaluation: $$evaluation" >&2; exit 1; }; \
		name="$$(basename "$$(dirname "$$evaluation")")"; \
		skill="$$(find "$(WAZA_PROJECTION_ROOT)/skills" -type d -name "$$name" -print)"; \
		test -n "$$skill" && test "$$(printf '%s\n' "$$skill" | wc -l)" -eq 1 || { \
			echo "projected skill owner is not unique: $$name" >&2; exit 1; \
		}; \
		env -C "$(WAZA_PROJECTION_ROOT)" $(MISE_EXEC) waza spec verify \
			--skill "$$skill" --eval "$$evaluation" --threshold 1 --fail --format human; \
		verified=$$((verified + 1)); \
	done; \
	test "$$verified" -eq "$$expected" || { \
		echo "Waza verified $$verified suites, expected $$expected" >&2; exit 1; \
	}; \
	printf 'Waza spec verification: %s suites\n' "$$verified"

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

fmt: ## apply canonical Python formatting; requires APPLY=Y
	$(call REQUIRE_APPLY)
	$(call BANNER,fmt · ruff format)
	@uv run ruff format src tests tools

fix: ## apply canonical corrections; requires APPLY=Y
	$(call REQUIRE_APPLY)
	$(call BANNER,fix · ruff)
	@uv run ruff check --fix src tests tools
	@for obsolete in $(OBSOLETE_LOCAL_PATHS); do \
		if [ -L "$$obsolete" ]; then \
			echo "refusing symlinked local cache: $$obsolete" >&2; exit 1; \
		elif [ -f "$$obsolete" ]; then \
			rm -- "$$obsolete"; \
		elif [ -d "$$obsolete" ]; then \
			rm -r -- "$$obsolete"; \
		elif [ -e "$$obsolete" ]; then \
			echo "refusing special local cache: $$obsolete" >&2; exit 1; \
		fi; \
	done

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
	@$(MAKE) mod-check APPLY=Y
	@$(MAKE) audit APPLY=Y

shell: ## validate shell scripts and GitHub workflows; requires APPLY=Y
	$(call REQUIRE_APPLY)
	$(call BANNER,shell · actionlint)
	@$(MISE_EXEC) actionlint .github/workflows/*.yml

duplication: ## enforce zero strict duplication in canonical Python source; requires APPLY=Y
	$(call REQUIRE_APPLY)
	$(call BANNER,duplication · jscpd)
	@$(MISE_EXEC) jscpd src tests tools --config $(CURDIR)/.jscpd.json --exit-code 1

build: ## build source and wheel artifacts; requires APPLY=Y
	$(call REQUIRE_APPLY)
	$(call BANNER,build · sdist + wheel)
	@mkdir -p "$(CURDIR)/dist"
	@find "$(CURDIR)/dist" -mindepth 1 -maxdepth 1 -type f ! -name .gitignore -delete
	@uv build

validate-wheel: ## validate the current built wheel in isolation; requires APPLY=Y
	$(call REQUIRE_APPLY)
	$(call BANNER,validate-wheel · installed public bundle)
	@wheel="$$(uv run python -c 'from pathlib import Path; import tomllib; project = tomllib.loads(Path("pyproject.toml").read_text())["project"]; print(Path("dist") / (project["name"].replace("-", "_") + "-" + project["version"] + "-py3-none-any.whl"))')"; \
		test -f "$$wheel"; \
		uv venv --clear "$(WHEEL_SMOKE)"; \
		uv pip install --python "$(WHEEL_SMOKE)/bin/python" "$$wheel"; \
		"$(WHEEL_SMOKE)/bin/python" -c 'from agents_governance import GovernanceBundle; bundle = GovernanceBundle.load(); print(bundle.distribution_version, bundle.schema_version)'

runtime: ## build, install, and load the public wheel; requires APPLY=Y
	$(call REQUIRE_APPLY)
	@$(MAKE) build APPLY=Y
	@$(MAKE) validate-wheel APPLY=Y

test: ## run affected tests through the shared testmon cache; requires APPLY=Y
	$(call REQUIRE_APPLY)
	$(call BANNER,test · pytest-testmon affected selection)
	$(call RUN_TESTMON,)

test-full: ## run incremental then all tests through the same cache; requires APPLY=Y
	$(call REQUIRE_APPLY)
	@$(MAKE) test APPLY=Y
	$(call BANNER,test-full · pytest-testmon no-selection)
	$(call RUN_TESTMON,--testmon-noselect)

## complete offline composition
ci: ## run every gate in runtime-first order; requires APPLY=Y
	$(call REQUIRE_APPLY)
	@$(MAKE) check APPLY=Y
	@$(MAKE) test-full APPLY=Y

## release publication
publish: ## publish the validated tag artifacts; requires APPLY=Y
	$(call REQUIRE_APPLY)
	$(call BANNER,publish · immutable GitHub release)
	@test -n "$$GITHUB_REF_NAME" || { echo 'GITHUB_REF_NAME is required' >&2; exit 2; }
	@test -n "$$GH_TOKEN" || { echo 'GH_TOKEN is required' >&2; exit 2; }
	@version="$$(uv run python -c 'from pathlib import Path; import tomllib; print(tomllib.loads(Path("pyproject.toml").read_text())["project"]["version"])')"; \
		test "$$GITHUB_REF_NAME" = "v$$version" || { \
			echo "release tag $$GITHUB_REF_NAME does not equal v$$version" >&2; exit 1; \
		}
	@$(MAKE) runtime APPLY=Y
	@cd "$(CURDIR)/dist" && sha256sum ./* > SHA256SUMS
	@gh release create "$$GITHUB_REF_NAME" --verify-tag --generate-notes "$(CURDIR)"/dist/*
