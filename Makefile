# ~/.agents skill authority — canonical execution surface.
# Every command runs here; no ad-hoc invocations (make-check law).
# UX: `make help` is the menu. Parameters: SKILL= APPLY= BASELINE= FOCUS= COUNT=.

PATH := $(HOME)/.local/bin:$(PATH)
export PATH

AGENTS_STORAGE_CONFIG ?= $(CURDIR)/config/storage.toml
export AGENTS_STORAGE_CONFIG

-include .env.local
include config/waza.mk
export

SKILL ?=
APPLY ?=
FOCUS ?=
COUNT ?=
PROJECT_ROOTS ?=
override RESULTS_DIR := results
BASELINE_DIR := $(RESULTS_DIR)/baseline
LATEST_DIR := $(RESULTS_DIR)/latest

SKILL_FILES := $(sort $(wildcard skills/*/*/SKILL.md))
SKILL_DIRS := $(patsubst %/SKILL.md,%,$(SKILL_FILES))
SKILLS := $(sort $(notdir $(SKILL_DIRS)))
skill_file = $(firstword $(filter %/$(1)/SKILL.md,$(SKILL_FILES)))
skill_dir = $(patsubst %/SKILL.md,%,$(call skill_file,$(1)))

.DEFAULT_GOAL := help
.PHONY: help status setup models audit check static fmt shell build ci security security-inventory temp sync adjust normalize descriptions test preflight validate-live rate baseline suggest spec coverage run gate compare validate clean
.DELETE_ON_ERROR:

define BANNER
	@if [ -z "$$NO_COLOR" ]; then printf '\033[1;36m▶\033[0m %s\n' "$(1)"; else printf '▶ %s\n' "$(1)"; fi
endef

help: ## show this menu (default)
	@awk 'BEGIN{FS=":.*## "} /^## /{sub(/^## */,""); gsub(/~/," "); print ""; $$1=$$1; print $$0} /^[a-z][a-z_-]*:.*## /{printf "  %-14s %s\n",$$1,$$2}' $(MAKEFILE_LIST)

## inspection
status: ## panel: tools, proxy, skills, baseline presence
	$(call BANNER,status · environment)
	@missing=0; for t in waza git awk; do command -v $$t >/dev/null && printf '  ok   %s\n' $$t || { printf '  MISS %s\n' $$t; missing=1; }; done; exit $$missing
	@$(WAZA_AUTHENTICATED) uv run agentsctl temp run -- sh -eu -c 'curl -fsS --max-time "$$WAZA_HTTP_TIMEOUT_SECONDS" -o /dev/null -H "Authorization: Bearer $$CLIPROXY_API_KEY" "$$COPILOT_PROVIDER_BASE_URL/models"' && echo "  ok   cliproxy $(CLIPROXY_BASE_URL)"
	@echo "  skills discovered: $(words $(SKILLS))"
	@if [ -f "$(BASELINE_DIR)/results.json" ]; then echo "  baseline: present ($(BASELINE_DIR)/results.json)"; else echo "  baseline: absent — run 'make baseline'"; fi

models: ## list judge models available through cliproxy
	$(call BANNER,models · via cliproxy $(COPILOT_PROVIDER_BASE_URL))
	@$(WAZA_AUTHENTICATED) uv run agentsctl temp run -- sh -eu -c 'catalog=$$(mktemp "$$TMPDIR/waza-models.XXXXXX.json"); curl -fsS --max-time "$$WAZA_HTTP_TIMEOUT_SECONDS" -H "Authorization: Bearer $$CLIPROXY_API_KEY" -o "$$catalog" "$$COPILOT_PROVIDER_BASE_URL/models"; uv run agentsctl waza-model-catalog "$$catalog"'

setup: ## idempotent project bootstrap (waza init + env sanity)
	$(call BANNER,setup · scaffold + env)
	@uv sync --all-groups
	@uv tool install --reinstall --offline --link-mode clone .
	@waza init --no-skill >/dev/null && echo "  waza init: ok"
	@$(WAZA_AUTHENTICATED) sh -eu -c 'printf "%s\n" "  judge credentials: available"'
	@printf '  judge model: ' && uv run agentsctl waza-config --model

audit: ## deterministic inventory; APPLY=Y refreshes skills.lock.json
	$(call BANNER,audit · canonical skill inventory)
	@uv run agentsctl audit $(if $(APPLY),--write,)

check: ## blocking local validation + strict Waza tokens
	$(call BANNER,check · agents authority $(if $(SKILL),[$(SKILL)],[all]))
	@uv run agentsctl validate $(if $(SKILL),--skill $(SKILL),)
	@uv run agentsctl waza-config --check
	@test -z "$(SKILL)" || test -n "$(call skill_dir,$(SKILL))" || { echo "unknown skill: $(SKILL)" >&2; exit 2; }
	@uv run agentsctl temp run -- waza tokens check $(if $(SKILL),$(call skill_dir,$(SKILL)),./skills) --strict
	@uv run agentsctl temp audit
	@uv run agentsctl normalize
	@uv run agentsctl descriptions

static: ## lint, format, and Python type analysis
	$(call BANNER,static · ruff + pyright + mypy)
	@uv run ruff check src tests
	@uv run ruff format --check src tests
	@uv run pyright src tests
	@uv run mypy src tests

fmt: ## apply canonical Python lint and format rewrites
	$(call BANNER,fmt · ruff)
	@uv run ruff check --fix src tests
	@uv run ruff format src tests

shell: ## shell scripts and GitHub workflow syntax
	$(call BANNER,shell · shellcheck + actionlint)
	@shellcheck hooks/*.sh
	@actionlint .github/workflows/*.yml

build: ## build source and wheel artifacts
	$(call BANNER,build · sdist + wheel)
	@uv run agentsctl temp run -- uv build

ci: ## complete offline CI pipeline
	$(call BANNER,ci · check + static + shell + build + test + spec + coverage + security inventory)
	@$(MAKE) --no-print-directory check
	@$(MAKE) --no-print-directory static
	@$(MAKE) --no-print-directory shell
	@$(MAKE) --no-print-directory build
	@$(MAKE) --no-print-directory test
	@$(MAKE) --no-print-directory spec
	@$(MAKE) --no-print-directory coverage
	@$(MAKE) --no-print-directory security-inventory

security-inventory: ## verify every tracked project manifest has one scanner route
	$(call BANNER,security · deterministic manifest inventory)
	@uv run agents-security inventory .

security: ## live secret, static-analysis, Snyk, and triage gates (all severities)
	$(call BANNER,security · all severities)
	@$(MAKE) --no-print-directory security-inventory
	@gitleaks dir --no-banner --exit-code 1 --redact .
	@semgrep scan --jobs 1 --config p/default --error --metrics=off --no-git-ignore --exclude .git --exclude .venv --exclude .cache --exclude .test-tmp --exclude results --exclude '$$HOME' .
	@uv run agents-security snyk .
	@uv run agentsctl security-triage .

temp: ## audit /tmp; STATUS=Y reports; APPLY=Y collects safe old owned runs
	$(call BANNER,temp · bounded scratch governance)
	@if [ -n "$(STATUS)" ]; then uv run agentsctl temp status; elif [ -n "$(APPLY)" ]; then uv run agentsctl temp gc --apply; else uv run agentsctl temp audit --global; fi

sync: ## check skills, commands, and rules projections; APPLY=Y reconciles
	$(call BANNER,sync · $(or $(SCOPE),personal) $(or $(SURFACE),all) copies $(if $(TARGET),[$(TARGET)],[all]))
	@uv run agentsctl project --scope $(or $(SCOPE),personal) --surface $(or $(SURFACE),all) $(if $(APPLY),--apply,--check) $(if $(TARGET),--target $(TARGET),) $(foreach root,$(PROJECT_ROOTS),--project-root $(root))

discover-projects: ## show automatic project capability classification
	$(call BANNER,discover · explicit project roots)
	@uv run agentsctl discover-projects $(foreach root,$(PROJECT_ROOTS),--project-root $(root))

adjust: ## Waza suggestions by default; APPLY=Y edits the canonical skill
	$(call BANNER,adjust · $(if $(SKILL),$(SKILL),MISSING SKILL=))
	@test -n "$(SKILL)" || { echo "usage: make adjust SKILL=<name> [APPLY=Y]"; exit 2; }
	@uv run agentsctl adjust --skill $(SKILL) $(if $(APPLY),--apply,)

normalize: ## report oversized SKILL.md files that need an authored router split
	$(call BANNER,normalize · progressive disclosure)
	@uv run agentsctl normalize $(if $(APPLY),--apply,)

descriptions: ## validate compact discovery keyword/nominal-phrase lists
	$(call BANNER,descriptions · discovery vocabulary)
	@uv run agentsctl descriptions $(if $(APPLY),--apply,)

test: ## unit tests for agentsctl
	$(call BANNER,test · agentsctl)
	@mkdir -p $(CURDIR)/.test-tmp/pytest
	@uv run pytest --basetemp $(CURDIR)/.test-tmp/pytest $(PYTEST_ARGS)
	@rmdir $(CURDIR)/.test-tmp/pytest

preflight: ## prove selected model, auth, Responses transport, tools, and artifact
	$(call BANNER,preflight · live Waza transport)
	@$(WAZA_AUTHENTICATED) uv run agentsctl waza-preflight

validate-live: preflight run gate compare ## preflight plus full live regression validation

rate: preflight ## AI judge 1-5 per dimension (or SKILL=name)
	$(call BANNER,rate · owner model $(if $(SKILL),[$(SKILL)],[all]))
ifeq ($(SKILL),)
	@set -eu; mkdir -p $(LATEST_DIR)/quality; failed=0; for skill_dir in $(SKILL_DIRS); do \
	  s=$${skill_dir##*/}; \
	  final=$(LATEST_DIR)/quality/$$s.json; candidate=$$(mktemp "$$final.XXXXXX.candidate"); echo "--- $$s"; \
	  if $(WAZA_ONLINE) quality "$$skill_dir" --format json > "$$candidate" && uv run agentsctl waza-artifact "$$candidate" --publish "$$final"; then :; \
	  else status=$$?; failed=1; echo "RATE FAILED ($$status): $$s → retry: make rate SKILL=$$s" >&2; fi; \
	  if [ -e "$$candidate" ] || [ -L "$$candidate" ]; then unlink "$$candidate" || { echo "RATE FAILED: candidate cleanup failed after status $${status:-0}: $$candidate" >&2; exit 70; }; fi; \
	done; exit $$failed
else
	@test -n "$(call skill_dir,$(SKILL))" || { echo "unknown skill: $(SKILL)" >&2; exit 2; }
	@mkdir -p $(LATEST_DIR)/quality
	@set -eu; final=$(LATEST_DIR)/quality/$(SKILL).json; candidate=$$(mktemp "$$final.XXXXXX.candidate"); \
	  if $(WAZA_ONLINE) quality "$(call skill_dir,$(SKILL))" --format json > "$$candidate" && uv run agentsctl waza-artifact "$$candidate" --publish "$$final"; then cat "$$final"; \
	  else status=$$?; if [ -e "$$candidate" ] || [ -L "$$candidate" ]; then unlink "$$candidate" || { echo "RATE FAILED: operation status $$status and candidate cleanup failed: $$candidate" >&2; exit 70; }; fi; exit $$status; fi
endif

baseline: preflight ## execute evals and write per-skill gate baselines
	$(call BANNER,baseline · snapshot → $(BASELINE_DIR))
	@mkdir -p $(BASELINE_DIR)
	@set -eu; final=$(BASELINE_DIR)/results.json; candidate=$$(mktemp "$$final.XXXXXX.candidate"); \
	  if $(WAZA_ONLINE) run skills --discover --strict --output "$$candidate" && uv run agentsctl waza-artifact "$$candidate" --publish "$$final"; then :; \
	  else status=$$?; if [ -e "$$candidate" ] || [ -L "$$candidate" ]; then unlink "$$candidate" || { echo "BASELINE FAILED: operation status $$status and candidate cleanup failed: $$candidate" >&2; exit 70; }; fi; exit $$status; fi

suggest: preflight ## propose evals (dry-run default; APPLY=1 writes, merge-safe)
	$(call BANNER,suggest · $(if $(SKILL),$(SKILL),MISSING SKILL=))
	@if [ -z "$(SKILL)" ]; then echo "  usage: make suggest SKILL=<name> [FOCUS=triggers|negative-triggers|edge-fixtures|do-not-use-for|parameters] [COUNT=n] [APPLY=1]"; exit 2; fi
	@test -n "$(call skill_dir,$(SKILL))" || { echo "unknown skill: $(SKILL)" >&2; exit 2; }
	@$(WAZA_ONLINE) suggest "$(call skill_dir,$(SKILL))" $(if $(APPLY),--apply,--dry-run) $(if $(FOCUS),--focus $(FOCUS)) $(if $(COUNT),--count $(COUNT))

spec: ## verify eval coverage vs SKILL.md requirements
	$(call BANNER,spec · coverage)
	@if [ -n "$(SKILL)" ]; then \
	  test -f "evals/$(SKILL)/eval.yaml" || { echo "missing eval: evals/$(SKILL)/eval.yaml"; exit 2; }; \
	  test -n "$(call skill_dir,$(SKILL))" || { echo "unknown skill: $(SKILL)"; exit 2; }; \
	  uv run agentsctl temp run -- waza spec verify --skill "$(call skill_dir,$(SKILL))" --eval "evals/$(SKILL)/eval.yaml" --fail; \
	else \
	  failed=0; for eval in evals/*/eval.yaml; do \
	    skill=$$(awk '$$1 == "skill:" { print $$2; exit }' "$$eval"); \
	    skill_file=$$(find skills -mindepth 3 -maxdepth 3 -type f -path "*/$$skill/SKILL.md" -print); \
	    test -n "$$skill" && test "$$(printf '%s\n' "$$skill_file" | sed '/^$$/d' | wc -l)" -eq 1 \
	      || { echo "invalid eval skill mapping: $$eval -> $${skill:-MISSING}"; failed=1; continue; }; \
	    skill_dir=$${skill_file%/SKILL.md}; \
	    uv run agentsctl temp run -- waza spec verify --skill "$$skill_dir" --eval "$$eval" --fail \
	      || failed=1; \
	  done; exit $$failed; \
	fi

coverage: ## require every canonical skill to have full Waza grader coverage
	$(call BANNER,coverage · all skills fully covered)
	@uv run agentsctl temp run -- sh -eu -c 'artifact=$$(mktemp "$$TMPDIR/coverage.XXXXXX.json"); \
	  waza coverage . --format json > "$$artifact"; \
	  uv run agentsctl waza-coverage "$$artifact"'

run: preflight ## execute eval benchmark (BASELINE=1 adds A/B with-vs-without skills)
	$(call BANNER,run · owner model $(if $(SKILL),[$(SKILL)],[discover all]))
	@mkdir -p $(LATEST_DIR)
	@set -eu; final=$(LATEST_DIR)/results.json; candidate=$$(mktemp "$$final.XXXXXX.candidate"); \
	  if $(WAZA_ONLINE) run $(if $(SKILL),evals/$(SKILL)/eval.yaml,skills --discover --strict) $(if $(BASELINE),--baseline) --output "$$candidate" && uv run agentsctl waza-artifact "$$candidate" --publish "$$final"; then :; \
	  else status=$$?; if [ -e "$$candidate" ] || [ -L "$$candidate" ]; then unlink "$$candidate" || { echo "RUN FAILED: operation status $$status and candidate cleanup failed: $$candidate" >&2; exit 70; }; fi; exit $$status; fi

gate: ## regression gate vs baseline (non-zero exit on regression)
	$(call BANNER,gate · vs $(BASELINE_DIR))
	@if [ ! -f "$(BASELINE_DIR)/results.json" ]; then echo "  no baseline results.json — run: make baseline"; exit 2; fi
	@if [ ! -f "$(LATEST_DIR)/results.json" ]; then echo "  no current results.json — run: make run"; exit 2; fi
	@uv run agentsctl waza-artifact $(BASELINE_DIR)/results.json
	@uv run agentsctl waza-artifact $(LATEST_DIR)/results.json
	@uv run agentsctl temp run -- waza gate --baseline $(BASELINE_DIR)/results.json --current $(LATEST_DIR)/results.json

compare: ## diff baseline vs latest scores
	$(call BANNER,compare · $(BASELINE_DIR) vs $(LATEST_DIR))
	@if [ ! -f "$(BASELINE_DIR)/results.json" ] || [ ! -f "$(LATEST_DIR)/results.json" ]; then echo "  baseline/current results.json missing"; exit 2; fi
	@uv run agentsctl waza-artifact $(BASELINE_DIR)/results.json
	@uv run agentsctl waza-artifact $(LATEST_DIR)/results.json
	@uv run agentsctl temp run -- waza compare $(BASELINE_DIR)/results.json $(LATEST_DIR)/results.json

validate: ## aggregate gate: check + spec + gate (stop on first red)
	$(call BANNER,validate · check→spec→gate)
	@$(MAKE) --no-print-directory check
	@$(MAKE) --no-print-directory spec
	@$(MAKE) --no-print-directory gate
	@if [ -z "$$NO_COLOR" ]; then printf '\033[1;32m✅ validate green\033[0m\n'; else echo "✅ validate green"; fi

clean: ## remove ONLY generated artifacts (.waza-cache, results/latest, pycache)
	$(call BANNER,clean · generated only)
	@uv run agentsctl clean
