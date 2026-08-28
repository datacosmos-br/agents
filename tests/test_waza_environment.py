"""Live Waza authentication accepts only the current process environment."""

from pathlib import Path


def test_live_waza_requires_the_canonical_environment_value() -> None:
    root = Path(__file__).parents[1]
    config = (root / "config" / "waza.mk").read_text(encoding="utf-8")

    assert "CLIPROXY_API_KEY:?CLIPROXY_API_KEY is required" in config
    assert 'COPILOT_PROVIDER_API_KEY="$$CLIPROXY_API_KEY"' in config
    assert 'COPILOT_MODEL="$$owner_model"' in config
