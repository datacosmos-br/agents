from pathlib import Path

import pytest

from agents_governance.agent_profiles import audit_agent_profiles
from agents_governance.catalog import Catalog
from agents_governance.commands import audit_command_specs
from agents_governance.native_evals import evaluate_native
from agents_governance.projection_config import load_projection_config
from agents_governance.rules import audit_rule_specs


def test_native_evals_render_every_supported_non_skill_artifact(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = Path(__file__).resolve().parents[1]
    catalog = Catalog(root)
    commands = audit_command_specs(root, (record.name for record in catalog.records()))
    monkeypatch.setattr(
        "agents_governance.native_evals.waza_bpe_counter",
        lambda _root: lambda content: len(content),
    )

    result = evaluate_native(
        root,
        load_projection_config(root),
        commands,
        audit_agent_profiles(root),
        audit_rule_specs(root),
    )

    assert result.commands >= len(commands)
    assert result.agents >= len(audit_agent_profiles(root))
    assert result.rules >= len(audit_rule_specs(root))
