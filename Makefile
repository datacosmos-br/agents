# ~/.agents skill authority — canonical execution surface.
# Every command runs here; no ad-hoc invocations (make-check law).
# UX: `make help` is the menu. Parameters: SKILL= MODEL= APPLY= BASELINE= FOCUS= COUNT=.

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
RESULTS_DIR ?= results
BASELINE_DIR := $(RESULTS_DIR)/baseline
LATEST_DIR := $(RESULTS_DIR)/latest

SKILLS := $(patsubst skills/%/SKILL.md,%,$(wildcard skills/*/SKILL.md))

.DEFAULT_GOAL := help
.PHONY: help status setup models audit check static shell build ci security temp sync mcp adjust normalize descriptions test preflight validate-live rate baseline suggest spec coverage run gate compare validate clean
.DELETE_ON_ERROR:

define BANNER
	@if [ -z "$$NO_COLOR" ]; then printf '\033[1;36m▶\033[0m %s\n' "$(1)"; else printf '▶ %s\n' "$(1)"; fi
endef

help: ## show this menu (default)
	@awk 'BEGIN{FS=":.*## "} /^## /{sub(/^## */,""); gsub(/~/," "); print ""; $$1=$$1; print $$0} /^[a-z][a-z_-]*:.*## /{printf "  %-14s %s\n",$$1,$$2}' $(MAKEFILE_LIST)

## inspection
status: ## panel: tools, proxy, skills, baseline presence
	$(call BANNER,status · environment)
	@for t in waza git awk; do command -v $$t >/dev/null && printf '  ok   %s\n' $$t || printf '  MISS %s\n' $$t; done
	@if $(WAZA_KEYRING_EXEC) sh -c 'curl -fsS -o /dev/null -m 2 -H "Authorization: Bearer $$CLIPROXY_API_KEY" "$$COPILOT_PROVIDER_BASE_URL/models"'; then echo "  ok   cliproxy :8317"; else echo "  DOWN cliproxy :8317"; fi
	@echo "  skills discovered: $(words $(SKILLS))"
	@if [ -f "$(BASELINE_DIR)/results.json" ]; then echo "  baseline: present ($(BASELINE_DIR)/results.json)"; else echo "  baseline: absent — run 'make baseline'"; fi

models: ## list judge models available through cliproxy
	$(call BANNER,models · via cliproxy $(if $(COPILOT_BASE_URL),$(COPILOT_BASE_URL),UNSET))
	@$(WAZA_KEYRING_EXEC) waza models

setup: ## idempotent project bootstrap (waza init + env sanity)
	$(call BANNER,setup · scaffold + env)
	@uv sync --all-groups
	@install -m 0755 bin/env-keyring bin/environment-d-loader "$(HOME)/.local/bin/"
	@waza init --no-skill >/dev/null && echo "  waza init: ok"
	@$(WAZA_KEYRING_EXEC) sh -c 'test -n "$$CLIPROXY_API_KEY"' && echo "  judge credentials: available"
	@echo "  judge model: $(if $(MODEL),$(MODEL),waza default)"

audit: ## deterministic inventory; APPLY=Y refreshes skills.lock.json
	$(call BANNER,audit · canonical skill inventory)
	@uv run agentsctl audit $(if $(APPLY),--write,)

check: ## blocking local validation + strict Waza tokens
	$(call BANNER,check · agents authority $(if $(SKILL),[$(SKILL)],[all]))
	@uv run agentsctl validate $(if $(SKILL),--skill $(SKILL),)
	@uv run agentsctl waza-config --check
	@uv run agentsctl temp run -- waza tokens check $(if $(SKILL),skills/$(SKILL),./skills) --strict
	@uv run agentsctl temp audit
	@uv run agentsctl normalize
	@uv run agentsctl descriptions

static: ## lint, format, and Python type analysis
	$(call BANNER,static · ruff + pyright + mypy)
	@uv run ruff check src tests
	@uv run ruff format --check src tests
	@uv run pyright src tests
	@uv run mypy src tests

shell: ## shell scripts and GitHub workflow syntax
	$(call BANNER,shell · shellcheck + actionlint)
	@shellcheck hooks/quality-gate.sh hooks/session-init.sh
	@actionlint .github/workflows/*.yml

build: ## build source and wheel artifacts
	$(call BANNER,build · sdist + wheel)
	@uv run agentsctl temp run -- uv build

ci: ## complete offline CI pipeline
	$(call BANNER,ci · check + static + shell + build + test + spec + coverage)
	@$(MAKE) --no-print-directory check
	@$(MAKE) --no-print-directory static
	@$(MAKE) --no-print-directory shell
	@$(MAKE) --no-print-directory build
	@$(MAKE) --no-print-directory test
	@$(MAKE) --no-print-directory spec
	@$(MAKE) --no-print-directory coverage

security: ## live secret, static-analysis, Snyk, and triage gates (all severities)
	$(call BANNER,security · all severities)
	@gitleaks dir --no-banner --exit-code 1 --redact .
	@semgrep scan --config p/default --error --metrics=off --no-git-ignore --exclude .git --exclude .venv --exclude .cache --exclude .test-tmp --exclude results --exclude '$$HOME' .
	@snyk test --all-projects --exclude=.venv,.cache,.test-tmp --severity-threshold=low
	@uv run agentsctl security-triage .

temp: ## audit /tmp; STATUS=Y reports; APPLY=Y collects safe old owned runs
	$(call BANNER,temp · bounded scratch governance)
	@if [ -n "$(STATUS)" ]; then uv run agentsctl temp status; elif [ -n "$(APPLY)" ]; then uv run agentsctl temp gc --apply; else uv run agentsctl temp audit --global; fi

sync: ## check skills, commands, and rules projections; APPLY=Y reconciles
	$(call BANNER,sync · $(or $(SCOPE),personal) $(or $(SURFACE),all) copies $(if $(TARGET),[$(TARGET)],[all]))
	@uv run agentsctl project --scope $(or $(SCOPE),personal) --surface $(or $(SURFACE),all) $(if $(APPLY),--apply,--check) $(if $(TARGET),--target $(TARGET),)

mcp: ## synchronize MCP through the canonical ai-hub owner
	$(call BANNER,mcp · ai-hub canonical sync $(if $(APPLY),[apply],[check]))
	@env-keyring auto-exec --directory "$(CURDIR)" --consumer agent:agents-mcp -- \
	  ai-hub mcp --action sync $(if $(APPLY),,--dry-run)

discover-projects: ## show automatic project/FLEXT/technology classification
	$(call BANNER,discover · configured project roots)
	@uv run agentsctl discover-projects

adjust: ## Waza suggestions by default; APPLY=Y edits the canonical skill
	$(call BANNER,adjust · $(if $(SKILL),$(SKILL),MISSING SKILL=))
	@test -n "$(SKILL)" || { echo "usage: make adjust SKILL=<name> [APPLY=Y]"; exit 2; }
	@uv run agentsctl adjust --skill $(SKILL) $(if $(APPLY),--apply,)

normalize: ## split oversized SKILL.md routers losslessly; APPLY=Y writes
	$(call BANNER,normalize · progressive disclosure)
	@uv run agentsctl normalize $(if $(APPLY),--apply,)

descriptions: ## compact skill descriptions to trigger keywords; APPLY=Y writes
	$(call BANNER,descriptions · keyword frontmatter)
	@uv run agentsctl descriptions $(if $(APPLY),--apply,)

test: ## unit tests for agentsctl
	$(call BANNER,test · agentsctl)
	@uv run agentsctl temp run -- sh -eu -c 'uv run pytest --basetemp "$$TMPDIR/pytest"'

preflight: ## prove selected model, auth, Responses transport, tools, and artifact
	$(call BANNER,preflight · live Waza transport)
	@mkdir -p $(RESULTS_DIR)/preflight; \
	  model="$(WAZA_MODEL)"; candidate=$(RESULTS_DIR)/preflight/results.json.candidate; \
	  $(WAZA_ONLINE) run config/waza/preflight/eval.yaml --model "$$model" --output "$$candidate"; \
	  uv run agentsctl waza-preflight --model "$$model" --output "$$candidate"; classified=$$?; \
	  if [ $$classified -eq 0 ]; then mv "$$candidate" $(RESULTS_DIR)/preflight/results.json; fi; \
	  exit $$classified

validate-live: preflight run gate compare ## preflight plus full live regression validation

rate: preflight ## AI judge 1-5 per dimension (or SKILL=name); MODEL= to override
	$(call BANNER,rate · judge=$(if $(MODEL),$(MODEL),waza-default) $(if $(SKILL),[$(SKILL)],[all]))
ifeq ($(SKILL),)
	@mkdir -p $(LATEST_DIR)/quality; failed=0; for s in $(SKILLS); do \
	  final=$(LATEST_DIR)/quality/$$s.json; candidate=$$final.candidate; echo "--- $$s"; mkdir -p $$(dirname $$final) && \
	  $(WAZA_ONLINE) quality skills/$$s $(MODEL_ARG) --format json > $$candidate && uv run agentsctl waza-artifact $$candidate && mv $$candidate $$final \
	    || { failed=1; echo "RATE FAILED: $$s → retry: make rate SKILL=$$s MODEL=$(MODEL)"; }; done; exit $$failed
else
	@mkdir -p $(LATEST_DIR)/quality
	@final=$(LATEST_DIR)/quality/$(SKILL).json; candidate=$$final.candidate; mkdir -p $$(dirname $$final) && \
	  $(WAZA_ONLINE) quality skills/$(SKILL) $(MODEL_ARG) --format json > $$candidate && \
	  uv run agentsctl waza-artifact $$candidate && mv $$candidate $$final && cat $$final
endif

baseline: preflight ## execute evals and write per-skill gate baselines
	$(call BANNER,baseline · snapshot → $(BASELINE_DIR))
	@mkdir -p $(BASELINE_DIR)
	@candidate=$(BASELINE_DIR)/results.json.candidate; \
	  $(WAZA_ONLINE) run skills --discover --strict $(MODEL_ARG) --output $$candidate && \
	  mv $$candidate $(BASELINE_DIR)/results.json

suggest: preflight ## propose evals (dry-run default; APPLY=1 writes, merge-safe)
	$(call BANNER,suggest · $(if $(SKILL),$(SKILL),MISSING SKILL=))
	@if [ -z "$(SKILL)" ]; then echo "  usage: make suggest SKILL=<name> [FOCUS=triggers|negative-triggers|edge-fixtures|do-not-use-for|parameters] [COUNT=n] [APPLY=1]"; exit 2; fi
	@$(WAZA_ONLINE) suggest skills/$(SKILL) $(if $(APPLY),--apply,--dry-run) $(if $(FOCUS),--focus $(FOCUS)) $(if $(COUNT),--count $(COUNT)) $(MODEL_ARG)

spec: ## verify eval coverage vs SKILL.md requirements
	$(call BANNER,spec · coverage)
	@if [ -n "$(SKILL)" ]; then \
	  test -f "evals/$(SKILL)/eval.yaml" || { echo "missing eval: evals/$(SKILL)/eval.yaml"; exit 2; }; \
	  uv run agentsctl temp run -- waza spec verify --skill "skills/$(SKILL)" --eval "evals/$(SKILL)/eval.yaml" --fail; \
	else \
	  failed=0; for eval in evals/*/eval.yaml; do \
	    skill=$$(awk '$$1 == "skill:" { print $$2; exit }' "$$eval"); \
	    test -n "$$skill" && test -f "skills/$$skill/SKILL.md" \
	      || { echo "invalid eval skill mapping: $$eval -> $${skill:-MISSING}"; failed=1; continue; }; \
	    uv run agentsctl temp run -- waza spec verify --skill "skills/$$skill" --eval "$$eval" --fail \
	      || failed=1; \
	  done; exit $$failed; \
	fi

coverage: ## require every canonical skill to have full Waza grader coverage
	$(call BANNER,coverage · all skills fully covered)
	@uv run agentsctl temp run -- sh -eu -c 'artifact=$$(mktemp "$$TMPDIR/coverage.XXXXXX.json"); \
	  trap '\''unlink "$$artifact"'\'' EXIT; \
	  waza coverage . --format json > "$$artifact"; \
	  uv run agentsctl waza-coverage "$$artifact"'

run: preflight ## execute eval benchmark (BASELINE=1 adds A/B with-vs-without skills)
	$(call BANNER,run · model=$(if $(MODEL),$(MODEL),waza-default) $(if $(SKILL),[$(SKILL)],[discover all]))
	@mkdir -p $(LATEST_DIR)
	@candidate=$(LATEST_DIR)/results.json.candidate; \
	  $(WAZA_ONLINE) run $(if $(SKILL),evals/$(SKILL)/eval.yaml,skills --discover --strict) $(MODEL_ARG) $(if $(BASELINE),--baseline) --output $$candidate && \
	  mv $$candidate $(LATEST_DIR)/results.json

gate: ## regression gate vs baseline (non-zero exit on regression)
	$(call BANNER,gate · vs $(BASELINE_DIR))
	@if [ ! -f "$(BASELINE_DIR)/results.json" ]; then echo "  no baseline results.json — run: make baseline"; exit 2; fi
	@if [ ! -f "$(LATEST_DIR)/results.json" ]; then echo "  no current results.json — run: make run"; exit 2; fi
	@uv run agentsctl temp run -- waza gate --baseline $(BASELINE_DIR)/results.json --current $(LATEST_DIR)/results.json

compare: ## diff baseline vs latest scores
	$(call BANNER,compare · $(BASELINE_DIR) vs $(LATEST_DIR))
	@if [ ! -f "$(BASELINE_DIR)/results.json" ] || [ ! -f "$(LATEST_DIR)/results.json" ]; then echo "  baseline/current results.json missing"; exit 2; fi
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
