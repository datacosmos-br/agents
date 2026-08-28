from __future__ import annotations

import pytest

from agents_governance.environment import required_environment


@pytest.mark.parametrize("value", [None, "", " ", "\t", "\n"])
def test_required_environment_rejects_missing_or_empty(
    monkeypatch: pytest.MonkeyPatch, value: str | None
) -> None:
    if value is None:
        monkeypatch.delenv("CLIPROXY_API_KEY", raising=False)
    else:
        monkeypatch.setenv("CLIPROXY_API_KEY", value)

    with pytest.raises(ValueError, match="CLIPROXY_API_KEY"):
        required_environment("CLIPROXY_API_KEY")


@pytest.mark.parametrize(
    "value",
    ["${CLIPROXY_API_KEY}", "$CLIPROXY_API_KEY", "%CLIPROXY_API_KEY%"],
)
def test_required_environment_rejects_unexpanded_values(
    monkeypatch: pytest.MonkeyPatch, value: str
) -> None:
    monkeypatch.setenv("CLIPROXY_API_KEY", value)

    with pytest.raises(ValueError, match="unexpanded"):
        required_environment("CLIPROXY_API_KEY")


def test_required_environment_rejects_conflicting_names(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CLIPROXY_API_KEY", "canonical")
    monkeypatch.setenv("COPILOT_PROVIDER_API_KEY", "foreign")

    with pytest.raises(ValueError, match="conflicting"):
        required_environment(
            "CLIPROXY_API_KEY", conflicts=("COPILOT_PROVIDER_API_KEY",)
        )


def test_required_environment_returns_the_exact_value(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CLIPROXY_API_KEY", "exact-value")
    monkeypatch.delenv("COPILOT_PROVIDER_API_KEY", raising=False)

    assert (
        required_environment(
            "CLIPROXY_API_KEY", conflicts=("COPILOT_PROVIDER_API_KEY",)
        )
        == "exact-value"
    )
