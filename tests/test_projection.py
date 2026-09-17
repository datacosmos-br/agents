"""Tests for the governance capsule projection pipeline.

These tests validate the determinism, idempotence, and content-addressed
integrity of the projection that renders the session capsule into provider
hook scripts, the OpenCode plugin, and instruction-pointer files. They
assert the derivation contract against the live bundle, never freeze
SSOT-declarable content.
"""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

from agents_governance import GovernanceBundle
from agents_governance.approvals import approval_tags
from agents_governance.capsule import (
    CAPSULE_MARKER,
    OPCODE_MARKER,
    Capsule,
    render_capsule,
)

_TOOLS = Path(__file__).resolve().parents[1] / "tools"


def _load_sync_governance():
    sys.path.insert(0, str(_TOOLS))
    import _projection  # noqa: F401
    spec = importlib.util.spec_from_file_location("_sync_governance", _TOOLS / "sync_governance.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["_sync_governance"] = module
    spec.loader.exec_module(module)
    return module


_sg = _load_sync_governance()


class TestsCapsuleRender:
    def test_capsule_body_has_header_marker(self, governance_bundle: GovernanceBundle) -> None:
        capsule = render_capsule(governance_bundle)
        assert capsule.body.startswith("# Generated session governance capsule")

    def test_digest_matches_body_sha256(self, governance_bundle: GovernanceBundle) -> None:
        capsule = render_capsule(governance_bundle)
        expected = hashlib.sha256(capsule.body.encode("utf-8")).hexdigest()
        assert capsule.digest == expected

    def test_header_embeds_digest(self, governance_bundle: GovernanceBundle) -> None:
        capsule = render_capsule(governance_bundle)
        expected = f"<!-- {CAPSULE_MARKER} sha256:{capsule.digest} -->"
        assert capsule.text.startswith(expected)

    def test_text_is_header_plus_body_plus_newline(self, governance_bundle: GovernanceBundle) -> None:
        capsule = render_capsule(governance_bundle)
        header_line = f"<!-- {CAPSULE_MARKER} sha256:{capsule.digest} -->"
        assert capsule.text == f"{header_line}\n{capsule.body}\n"

    def test_opencode_digest_matches_full_text(self, governance_bundle: GovernanceBundle) -> None:
        capsule = render_capsule(governance_bundle)
        expected = hashlib.sha256(capsule.text.encode("utf-8")).hexdigest()
        assert capsule.opencode_digest == expected

    def test_render_is_deterministic(self, governance_bundle: GovernanceBundle) -> None:
        first = render_capsule(governance_bundle)
        second = render_capsule(governance_bundle)
        assert first.text == second.text
        assert first.digest == second.digest

    def test_all_bootstrap_rules_present(self, governance_bundle: GovernanceBundle) -> None:
        capsule = render_capsule(governance_bundle)
        for ident in governance_bundle.config.bootstrap_rules:
            assert f"## Rule `{ident}`" in capsule.body

    def test_bootstrap_rules_have_approval_tags(self, governance_bundle: GovernanceBundle) -> None:
        capsule = render_capsule(governance_bundle)
        by_identity = {rule.identity: rule for rule in governance_bundle.rules}
        for ident in governance_bundle.config.bootstrap_rules:
            rule = by_identity[ident]
            approves = approval_tags(rule.tags)
            for tag in approves:
                assert tag in capsule.body

    def test_bootstrap_skills_listed_by_name(self, governance_bundle: GovernanceBundle) -> None:
        capsule = render_capsule(governance_bundle)
        for name in governance_bundle.config.bootstrap_skills:
            assert name in capsule.body

    def test_all_commands_listed(self, governance_bundle: GovernanceBundle) -> None:
        capsule = render_capsule(governance_bundle)
        for cmd in governance_bundle.commands:
            assert cmd.name in capsule.body

    def test_capsule_within_delivery_budget(self, governance_bundle: GovernanceBundle) -> None:
        capsule = render_capsule(governance_bundle)
        budget = governance_bundle.config.delivery.capsule_budget_chars
        reserve = governance_bundle.config.delivery.restore_list_reserve_chars
        ceiling = budget - reserve
        assert governance_bundle.delivery.total_chars <= ceiling
        assert len(capsule.body) <= ceiling


class TestsPythonHookRendering:
    @pytest.fixture
    def capsule(self, governance_bundle: GovernanceBundle) -> Capsule:
        return render_capsule(governance_bundle)

    def test_codex_hook_emits_capsule(self, capsule: Capsule) -> None:
        response = {"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": capsule.text}}
        script = _sg._render_python_hook(response)
        result = subprocess.run(
            [sys.executable, "-c", script],
            input=json.dumps({}),
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0, result.stderr
        output = json.loads(result.stdout)
        assert output["hookSpecificOutput"]["additionalContext"] == capsule.text

    def test_cursor_hook_format(self, capsule: Capsule) -> None:
        response = {"additional_context": capsule.text}
        script = _sg._render_python_hook(response)
        result = subprocess.run(
            [sys.executable, "-c", script],
            input=json.dumps({}),
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0, result.stderr
        output = json.loads(result.stdout)
        assert output["additional_context"] == capsule.text

    def test_empty_response_hook(self) -> None:
        script = _sg._render_python_hook({})
        result = subprocess.run(
            [sys.executable, "-c", script],
            input=json.dumps({}),
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0, result.stderr
        assert json.loads(result.stdout) == {}


class TestsOpenCodePlugin:
    def test_plugin_has_correct_digest(self, governance_bundle: GovernanceBundle) -> None:
        capsule = render_capsule(governance_bundle)
        output = _sg._render_opencode_plugin(capsule)
        assert f'const DIGEST = "{capsule.opencode_digest}"' in output
        assert OPCODE_MARKER in output

    def test_plugin_capsule_literal_matches(self, governance_bundle: GovernanceBundle) -> None:
        capsule = render_capsule(governance_bundle)
        output = _sg._render_opencode_plugin(capsule)
        assert json.dumps(capsule.text, ensure_ascii=False) in output


class TestsProjectionFixedPoint:
    def test_projection_is_fixed_point(
        self, governance_bundle: GovernanceBundle, tmp_path: Path
    ) -> None:
        capsule = render_capsule(governance_bundle)
        first = tmp_path / "first"
        second = tmp_path / "second"
        first.mkdir()
        second.mkdir()
        _sg._build(first, capsule)
        _sg._build(second, capsule)
        assert _snapshot_dir(first) == _snapshot_dir(second)

    def test_all_capsule_hooks_share_same_digest(
        self, governance_bundle: GovernanceBundle, tmp_path: Path
    ) -> None:
        capsule = render_capsule(governance_bundle)
        root = tmp_path / "out"
        root.mkdir()
        _sg._build_hooks(root, capsule)
        digests: set[str] = set()
        for hook in _sg._HOOKS:
            content = (root / hook.relpath).read_text(encoding="utf-8")
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if (
                    isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Attribute)
                    and node.func.attr == "loads"
                ):
                    data = json.loads(node.args[0].value)
                    flat = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
                    if CAPSULE_MARKER in flat:
                        digests.add(hashlib.sha256(flat.encode("utf-8")).hexdigest())
        assert len(digests) == 1, f"digest mismatch across capsule hooks: {digests}"


class TestsManifestConsistency:
    def test_all_manifests_match_files(
        self, governance_bundle: GovernanceBundle, tmp_path: Path
    ) -> None:
        capsule = render_capsule(governance_bundle)
        root = tmp_path / "out"
        root.mkdir()
        _sg._build(root, capsule)
        manifests = [
            root / ".codex/.hooks.json.agents-governance.json",
            root / ".gemini/.settings.json.agents-governance.json",
            root / ".cursor/.hooks.json.agents-governance.json",
            root / ".opencode/plugins/.aihub-governance.ts.agents-governance.json",
        ]
        for manifest_path in manifests:
            assert manifest_path.is_file(), f"manifest missing: {manifest_path}"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            for relpath, info in manifest.get("managed", {}).items():
                actual = hashlib.sha256((root / relpath).read_bytes()).hexdigest()
                assert actual == info["digest"], f"{manifest_path}: digest mismatch for {relpath}"


class TestsInstructionPointers:
    def test_claude_md_content(self, governance_bundle: GovernanceBundle, tmp_path: Path) -> None:
        root = tmp_path / "out"
        root.mkdir()
        _sg._build_instructions(root)
        content = (root / "CLAUDE.md").read_text(encoding="utf-8")
        assert "AGENTS.md" in content
        assert "make gen" in content
        assert "AIHUB-INSTRUCTION-POINTER" in content

    def test_gemini_md_content(self, governance_bundle: GovernanceBundle, tmp_path: Path) -> None:
        root = tmp_path / "out"
        root.mkdir()
        _sg._build_instructions(root)
        content = (root / "GEMINI.md").read_text(encoding="utf-8")
        assert "AGENTS.md" in content
        assert "make gen" in content


def _snapshot_dir(root: Path) -> tuple[tuple[str, str], ...]:
    entries: list[tuple[str, str]] = []
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink() or not (path.is_dir() or path.is_file()):
            raise ValueError(f"non-physical path: {path}")
        digest = "directory" if path.is_dir() else hashlib.sha256(path.read_bytes()).hexdigest()
        entries.append((relative, digest))
    return tuple(entries)
