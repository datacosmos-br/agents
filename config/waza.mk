# Waza's OpenAI-compatible judge transport through the locally managed CLIPROXY.
CLIPROXY_BASE_URL ?= http://127.0.0.1:8317

COPILOT_PROVIDER_BASE_URL ?= $(CLIPROXY_BASE_URL)/v1
COPILOT_PROVIDER_TYPE ?= openai
COPILOT_PROVIDER_WIRE_API ?= responses

export COPILOT_PROVIDER_BASE_URL COPILOT_PROVIDER_TYPE
export COPILOT_PROVIDER_WIRE_API

MODEL ?=
WAZA_MODEL = $(if $(strip $(MODEL)),$(MODEL),$$(uv run agentsctl waza-config --model))
MODEL_ARG = --model $(WAZA_MODEL)

WAZA_KEYRING_EXEC = env-keyring auto-exec --directory "$(CURDIR)" --consumer agent:agents-waza --
WAZA_ONLINE = $(WAZA_KEYRING_EXEC) env COPILOT_MODEL="$(WAZA_MODEL)" uv run agentsctl temp run -- waza
