# Waza's OpenAI-compatible judge transport through the locally managed CLIPROXY.
CLIPROXY_BASE_URL ?= http://127.0.0.1:8317
CLIPROXY_AUTH_FILE ?= $(HOME)/.config/environment
CLIPROXY_API_KEY ?= $(shell awk -F= '$$1 == "CLIPROXY_API_KEY" { sub(/^[^=]*=/, ""); print; exit }' $(CLIPROXY_AUTH_FILE) 2>/dev/null)

COPILOT_PROVIDER_BASE_URL ?= $(CLIPROXY_BASE_URL)/v1
COPILOT_PROVIDER_TYPE ?= openai
COPILOT_PROVIDER_WIRE_API ?= completions
COPILOT_PROVIDER_API_KEY ?= $(CLIPROXY_API_KEY)

export COPILOT_PROVIDER_BASE_URL COPILOT_PROVIDER_TYPE
export COPILOT_PROVIDER_WIRE_API COPILOT_PROVIDER_API_KEY

MODEL ?= gpt-5.4
MODEL_ARG = $(if $(strip $(MODEL)),--model $(MODEL),)
COPILOT_MODEL ?= $(MODEL)
export COPILOT_MODEL
