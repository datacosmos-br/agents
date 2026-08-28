# Waza's OpenAI-compatible judge transport through the locally managed CLIPROXY.
override CLIPROXY_BASE_URL := http://127.0.0.1:8317

override COPILOT_PROVIDER_BASE_URL := $(CLIPROXY_BASE_URL)/v1
override COPILOT_PROVIDER_TYPE := openai
override COPILOT_PROVIDER_WIRE_API := responses
override WAZA_HTTP_TIMEOUT_SECONDS := 10

export COPILOT_PROVIDER_BASE_URL COPILOT_PROVIDER_TYPE
export COPILOT_PROVIDER_WIRE_API WAZA_HTTP_TIMEOUT_SECONDS

override WAZA_KEYRING_EXEC = env-keyring auto-exec --directory "$(CURDIR)" --consumer agent:agents-waza --
override WAZA_AUTHENTICATED = $(WAZA_KEYRING_EXEC) sh -eu -c 'owner_model=$$(uv run agentsctl waza-config --model); export COPILOT_PROVIDER_API_KEY="$$CLIPROXY_API_KEY"; export COPILOT_MODEL="$$owner_model"; exec "$$@"' --
override WAZA_ONLINE = $(WAZA_KEYRING_EXEC) sh -eu -c 'owner_model=$$(uv run agentsctl waza-config --model); export COPILOT_PROVIDER_API_KEY="$$CLIPROXY_API_KEY"; export COPILOT_MODEL="$$owner_model"; exec uv run agentsctl temp run -- waza "$$@" --model "$$owner_model"' --
