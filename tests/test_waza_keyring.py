"""Waza online commands must receive credentials only through the keyring owner."""

from pathlib import Path


def test_waza_auth_uses_automatic_keyring_execution() -> None:
    """Prevent file scraping or ambient-secret fallbacks from returning."""
    root = Path(__file__).parents[1]
    config = (root / "config" / "waza.mk").read_text(encoding="utf-8")
    makefile = (root / "Makefile").read_text(encoding="utf-8")

    assert "env-keyring auto-exec" in config
    assert "agent:agents-waza" in config
    assert "CLIPROXY_AUTH_FILE" not in config
    assert "awk -F=" not in config
    assert "COPILOT_PROVIDER_API_KEY ?=" not in config
    assert "$(WAZA_ONLINE) quality" in makefile
    assert "$(WAZA_ONLINE) run" in makefile
    assert "$(WAZA_ONLINE) suggest" in makefile
