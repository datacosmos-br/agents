import pytest

from delivery.worker import timeout_for


def test_email_uses_declared_policy() -> None:
    assert timeout_for("email") == 5


def test_unknown_channel_fails_explicitly() -> None:
    with pytest.raises(ValueError, match="unsupported channel: fax"):
        timeout_for("fax")
