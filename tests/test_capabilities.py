from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import pytest

from agents_governance import runtime
from agents_governance.catalog import Catalog
from agents_governance.cleanup import Publication

ROOT = Path(__file__).resolve().parents[1]


def _unexpected(name: str) -> object:
    raise AssertionError(f"dormant capability was loaded: {name}")


def test_base_inventory_does_not_load_auxiliary_capabilities(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(runtime, "_catalog", lambda root: Catalog(root))
    monkeypatch.setattr(
        runtime,
        "load_projection_config",
        lambda _root: _unexpected("projection"),
    )
    monkeypatch.setattr(
        runtime,
        "require_model_projection",
        lambda _root: _unexpected("live model"),
    )
    monkeypatch.setattr(
        runtime,
        "security_inventory",
        lambda _roots: _unexpected("security scanner"),
    )
    monkeypatch.setattr(
        runtime,
        "audit_security_evidence",
        lambda _roots: _unexpected("security evidence"),
    )

    inventory = runtime._inventory(ROOT)

    assert inventory.commands
    assert inventory.agents
    assert inventory.rules
    assert not hasattr(inventory, "projection")
    assert not hasattr(inventory, "model")
    assert not hasattr(inventory, "security_routes")


def test_additive_capability_rule_is_in_the_generated_session_capsule(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(runtime, "_catalog", lambda root: Catalog(root))
    inventory = runtime._inventory(ROOT)
    home = tmp_path / "home"
    project = tmp_path / "project"
    home.mkdir()
    project.mkdir()
    selection = project / ".agents" / "projection.json"
    selection.parent.mkdir()
    selection.write_text(
        '{"agents":[],"opt_ins":[],"selected_tags":[],"version":1}',
        encoding="utf-8",
    )
    monkeypatch.setenv("HOME", str(home))
    hooks = runtime.HookProjector(
        inventory.governance,
        runtime.load_projection_config(ROOT),
        inventory.commands,
        inventory.rules,
    )

    hooks.apply(project)

    script = next((project / ".codex" / "aihub-hooks").glob("*.py"))
    rendered = script.read_text(encoding="utf-8")
    assert "Auxiliary tracking" in rendered
    assert "strict execution" in rendered
    assert "[strict execution](" not in rendered


def test_sync_selects_projection_without_live_or_security(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    events: list[str] = []
    authorize = runtime.load_project_authorization
    publish = runtime.run_atomic_publications

    def record_authorization(project: Path) -> object:
        events.append("authorization")
        return authorize(project)

    def record_publication(publications: Sequence[Publication]) -> None:
        events.append("publication")
        publish(publications)

    def record_lock(_destination: Path, _text: str) -> None:
        events.append("lock")

    monkeypatch.setattr(runtime, "_catalog", lambda root: Catalog(root))
    inventory = runtime._inventory(ROOT)
    monkeypatch.setattr(runtime, "Catalog", lambda _root: inventory.catalog)
    monkeypatch.setattr(
        runtime,
        "_inventory_from_catalog",
        lambda _root, _catalog: inventory,
    )
    monkeypatch.setattr(
        runtime,
        "require_model_projection",
        lambda _root: _unexpected("live model"),
    )
    monkeypatch.setattr(
        runtime,
        "security_inventory",
        lambda _roots: _unexpected("security scanner"),
    )
    monkeypatch.setattr(runtime, "load_project_authorization", record_authorization)
    monkeypatch.setattr(runtime, "text_publication", record_lock)
    monkeypatch.setattr(runtime, "run_atomic_publications", record_publication)
    home = tmp_path / "home"
    project = tmp_path / "project"
    home.mkdir()
    project.mkdir()
    (project / ".git").mkdir()
    selection = project / ".agents" / "projection.json"
    selection.parent.mkdir()
    selection.write_text(
        '{"agents":[],"opt_ins":[],"selected_tags":[],"version":1}',
        encoding="utf-8",
    )
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.chdir(project)
    assert Path.home().resolve(strict=True) == home

    runtime.sync(ROOT)

    assert (home / ".codex" / "hooks.json").is_file()
    assert (project / ".codex" / "hooks.json").is_file()
    assert events == ["authorization", "lock", "publication"]
    assert capsys.readouterr().out == (
        f"sync: personal and project projections converged at {project}\n"
    )


def test_sync_reuses_one_project_authorization_snapshot(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(runtime, "_catalog", lambda root: Catalog(root))
    inventory = runtime._inventory(ROOT)
    monkeypatch.setattr(runtime, "Catalog", lambda _root: inventory.catalog)
    monkeypatch.setattr(
        runtime,
        "_inventory_from_catalog",
        lambda _root, _catalog: inventory,
    )
    monkeypatch.setattr(runtime, "text_publication", lambda _path, _text: None)
    home = tmp_path / "home"
    project = tmp_path / "project"
    home.mkdir()
    project.mkdir()
    (project / ".git").mkdir()
    selection = project / ".agents" / "projection.json"
    selection.parent.mkdir()
    selection.write_text(
        '{"agents":[],"opt_ins":[],"selected_tags":[],"version":1}',
        encoding="utf-8",
    )
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.chdir(project)
    original = runtime.Projector.publications

    def mutate_after_static_preflight(projector: object, *args: object) -> object:
        publications = original(projector, *args)  # type: ignore[arg-type]
        selection.unlink()
        return publications

    monkeypatch.setattr(
        runtime.Projector, "publications", mutate_after_static_preflight
    )

    runtime.sync(ROOT)

    assert (project / ".codex" / "hooks.json").is_file()


def test_sync_reports_an_unselected_project_as_a_non_target(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(runtime, "_catalog", lambda root: Catalog(root))
    inventory = runtime._inventory(ROOT)
    monkeypatch.setattr(runtime, "Catalog", lambda _root: inventory.catalog)
    monkeypatch.setattr(
        runtime,
        "_inventory_from_catalog",
        lambda _root, _catalog: inventory,
    )
    monkeypatch.setattr(runtime, "text_publication", lambda _path, _text: None)
    home = tmp_path / "home"
    project = tmp_path / "project"
    home.mkdir()
    project.mkdir()
    (project / ".git").mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.chdir(project)

    runtime.sync(ROOT)

    assert (home / ".codex" / "hooks.json").is_file()
    assert not (project / ".codex").exists()
    assert capsys.readouterr().out == (
        f"sync: personal projections converged; project not selected at {project}\n"
    )
