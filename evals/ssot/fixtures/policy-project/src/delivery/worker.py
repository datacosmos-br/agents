from __future__ import annotations

from delivery.generated_policy import TIMEOUT_SECONDS

EMAIL_TIMEOUT_SECONDS = 4


def timeout_for(channel: str) -> int:
    if channel == "email":
        return EMAIL_TIMEOUT_SECONDS
    if channel not in TIMEOUT_SECONDS:
        raise ValueError(f"unsupported channel: {channel}")
    return TIMEOUT_SECONDS[channel]
