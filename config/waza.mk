# Waza's OpenAI-compatible judge transport through the locally managed CLIPROXY.
CLIPROXY_BASE_URL ?= http://127.0.0.1:8317

COPILOT_PROVIDER_BASE_URL ?= $(CLIPROXY_BASE_URL)/v1
COPILOT_PROVIDER_TYPE ?= openai
COPILOT_PROVIDER_WIRE_API ?= completions

export COPILOT_PROVIDER_BASE_URL COPILOT_PROVIDER_TYPE
export COPILOT_PROVIDER_WIRE_API

WAZA_KEYRING_EXEC = env-keyring auto-exec --directory "$(CURDIR)" --consumer agent:agents-waza --
WAZA_ONLINE = $(WAZA_KEYRING_EXEC) uv run agentsctl temp run -- waza

MODEL ?= gpt-5.4
MODEL_ARG = $(if $(strip $(MODEL)),--model $(MODEL),)
COPILOT_MODEL ?= $(MODEL)
export COPILOT_MODEL
