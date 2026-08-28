import pytest

from retries.worker import attempts_for


def test_email_uses_declared_policy() -> None:
    assert attempts_for("email") == 5


def test_unknown_channel_fails_explicitly() -> None:
    with pytest.raises(ValueError, match="unsupported channel: fax"):
        attempts_for("fax")
