from pathlib import Path

from agents_governance.dolt import audit, repair


def test_audit_accepts_only_canonical_endpoint(tmp_path: Path) -> None:
    beads = tmp_path / "rig" / ".beads"
    beads.mkdir(parents=True)
    (beads / "config.yaml").write_text('dolt.port: "3307"\n', encoding="utf-8")
    (beads / "metadata.json").write_text(
        '{"dolt_server_host":"127.0.0.1","dolt_server_port":3307}\n', encoding="utf-8"
    )

    assert audit(tmp_path, environ={}, proc=tmp_path / "missing-proc") == []


def test_audit_rejects_shared_server_metadata_env_and_live_listener(
    tmp_path: Path,
) -> None:
    beads = tmp_path / "rig" / ".beads"
    beads.mkdir(parents=True)
    (beads / "config.yaml").write_text(
        "dolt:\n  shared-server: true\n  port: 3308\n", encoding="utf-8"
    )
    (beads / "metadata.json").write_text(
        '{"dolt_server_host":"10.0.0.8","dolt_server_port":3309}\n', encoding="utf-8"
    )
    proc = tmp_path / "proc" / "42"
    proc.mkdir(parents=True)
    (proc / "cmdline").write_bytes(
        b"dolt\0sql-server\0-H\0" + b"127.0.0.1\0-P\0" + b"38085\0"
    )

    findings = audit(
        tmp_path,
        environ={"BEADS_DOLT_SHARED_SERVER": "true", "GT_DOLT_PORT": "3310"},
        proc=tmp_path / "proc",
    )

    assert {item.code for item in findings} == {
        "shared-server",
        "noncanonical-port",
        "noncanonical-host",
        "noncanonical-listener",
    }


def test_audit_rejects_embedded_dolt(tmp_path: Path) -> None:
    beads = tmp_path / "rig" / ".beads"
    beads.mkdir(parents=True)
    (beads / "metadata.json").write_text(
        '{"backend":"dolt","dolt_mode":"embedded","dolt_database":"rig"}\n',
        encoding="utf-8",
    )

    findings = audit(tmp_path, environ={}, proc=tmp_path / "missing-proc")

    assert [item.code for item in findings] == ["noncanonical-mode"]


def test_audit_does_not_exempt_test_scratch(tmp_path: Path) -> None:
    beads = tmp_path / ".test-tmp" / "fixture" / ".beads"
    beads.mkdir(parents=True)
    (beads / "metadata.json").write_text(
        '{"backend":"dolt","dolt_mode":"embedded","dolt_database":"fixture"}\n',
        encoding="utf-8",
    )

    findings = audit(tmp_path, environ={}, proc=tmp_path / "missing-proc")

    assert [item.code for item in findings] == ["noncanonical-mode"]


def test_repair_converges_config_and_embedded_metadata(tmp_path: Path) -> None:
    beads = tmp_path / "rig" / "crew" / "worker" / ".beads"
    beads.mkdir(parents=True)
    (beads / "config.yaml").write_text(
        "dolt:\n  shared-server: true\n  port: 3308\n", encoding="utf-8"
    )
    (beads / "metadata.json").write_text(
        '{"backend":"dolt","dolt_mode":"embedded","dolt_database":"wrong"}\n',
        encoding="utf-8",
    )

    assert len(repair(tmp_path)) == 2
    assert audit(tmp_path, environ={}, proc=tmp_path / "missing-proc") == []
    payload = __import__("json").loads(
        (beads / "metadata.json").read_text(encoding="utf-8")
    )
    assert payload["dolt_database"] == "rig"
    assert payload["dolt_server_port"] == 3307


def test_audit_includes_global_beads_config(tmp_path: Path) -> None:
    town = tmp_path / "gt"
    town.mkdir()
    global_beads = tmp_path / ".beads"
    global_beads.mkdir()
    (global_beads / "config.yaml").write_text(
        "dolt:\n  shared-server: true\n", encoding="utf-8"
    )

    findings = audit(town, environ={}, proc=tmp_path / "missing-proc")

    assert [item.code for item in findings] == ["shared-server"]


def test_audit_rejects_unguarded_installed_dolt(tmp_path: Path) -> None:
    town = tmp_path / "gt"
    town.mkdir()
    binary = tmp_path / ".local/share/mise/installs/github-dolt-hub-dolt/2.3.1/bin/dolt"
    binary.parent.mkdir(parents=True)
    binary.write_bytes(b"raw executable")

    findings = audit(town, environ={}, proc=tmp_path / "missing-proc")

    assert {item.code for item in findings} == {
        "unguarded-binary",
        "missing-owned-binary",
    }
