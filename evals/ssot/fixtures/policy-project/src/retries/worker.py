from __future__ import annotations

from retries.generated_policy import MAX_ATTEMPTS

EMAIL_MAX_ATTEMPTS = 4


def attempts_for(channel: str) -> int:
    if channel == "email":
        return EMAIL_MAX_ATTEMPTS
    try:
        return MAX_ATTEMPTS[channel]
    except KeyError as error:
        raise ValueError(f"unsupported channel: {channel}") from error
