# Video Recording

Capture browser automation sessions as video for debugging, documentation, or verification.

## Basic Recording

```bash
# Start recording
agent-browser record start ./demo.webm

# Perform actions
agent-browser open https://example.com
agent-browser snapshot -i
agent-browser click @e1
agent-browser fill @e2 "test input"

# Stop and save
agent-browser record stop
```

## Recording Commands

```bash
# Start recording to file
agent-browser record start ./output.webm

# Stop current recording
agent-browser record stop

# Restart with new file (stops current + starts new)
agent-browser record restart ./take2.webm
```

## Use Cases

### Debugging Failed Automation

```bash
#!/bin/bash
# Record automation for debugging
set -euo pipefail

agent-browser record start ./debug-$(date +%Y%m%d-%H%M%S).webm

# Run your automation
agent-browser open https://app.example.com
agent-browser snapshot -i
click_status=0
agent-browser click @e1 || click_status=$?
if (( click_status != 0 )); then
    echo "ERROR: click failed; check recording" >&2
    stop_status=0
    agent-browser record stop || stop_status=$?
    if (( stop_status != 0 )); then
        echo "ERROR: recording cleanup failed with status $stop_status" >&2
    fi
    exit "$click_status"
fi

agent-browser record stop
```

### Documentation Generation

```bash
#!/bin/bash
# Record workflow for documentation
set -euo pipefail

agent-browser record start ./docs/how-to-login.webm

agent-browser open https://app.example.com/login
agent-browser wait 1000  # Pause for visibility

agent-browser snapshot -i
agent-browser fill @e1 "demo@example.com"
agent-browser wait 500

agent-browser fill @e2 "password"
agent-browser wait 500

agent-browser click @e3
agent-browser wait --load networkidle
agent-browser wait 1000  # Show result

agent-browser record stop
```

### CI/CD Test Evidence

```bash
#!/bin/bash
# Record E2E test runs for CI artifacts
set -euo pipefail

TEST_NAME="${1:-e2e-test}"
RECORDING_DIR="./test-recordings"
mkdir -p "$RECORDING_DIR"

agent-browser record start "$RECORDING_DIR/$TEST_NAME-$(date +%s).webm"

# Run test
test_status=0
run_e2e_test || test_status=$?
if (( test_status == 0 )); then
    echo "Test passed"
else
    echo "Test failed - recording saved"
fi

stop_status=0
agent-browser record stop || stop_status=$?
if (( stop_status != 0 )); then
    echo "ERROR: recording cleanup failed with status $stop_status" >&2
fi
if (( test_status != 0 )); then
    exit "$test_status"
fi
exit "$stop_status"
```

## Best Practices

### 1. Add Pauses for Clarity

```bash
# Slow down for human viewing
agent-browser click @e1
agent-browser wait 500  # Let viewer see result
```

### 2. Use Descriptive Filenames

```bash
# Include context in filename
agent-browser record start ./recordings/login-flow-2024-01-15.webm
agent-browser record start ./recordings/checkout-test-run-42.webm
```

### 3. Handle Recording in Error Cases

```bash
#!/bin/bash
set -euo pipefail

cleanup() {
    local operation_status=$?
    local stop_status=0
    local close_status=0

    trap - EXIT
    agent-browser record stop || stop_status=$?
    agent-browser close || close_status=$?
    if (( operation_status != 0 )); then
        exit "$operation_status"
    fi
    if (( stop_status != 0 )); then
        exit "$stop_status"
    fi
    exit "$close_status"
}
trap cleanup EXIT

agent-browser record start ./automation.webm
# ... automation steps ...
```

### 4. Combine with Screenshots

```bash
# Record video AND capture key frames
agent-browser record start ./flow.webm

agent-browser open https://example.com
agent-browser screenshot ./screenshots/step1-homepage.png

agent-browser click @e1
agent-browser screenshot ./screenshots/step2-after-click.png

agent-browser record stop
```

## Output Format

- Default format: WebM (VP8/VP9 codec)
- Compatible with all modern browsers and video players
- Compressed but high quality

## Limitations

- Recording adds slight overhead to automation
- Large recordings can consume significant disk space
- Some headless environments may have codec limitations
