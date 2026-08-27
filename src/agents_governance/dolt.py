"""Fail-closed audit for the single Gas Town Dolt endpoint."""

from __future__ import annotations

import json
import os
import re
import stat
from dataclasses import asdict, dataclass
from pathlib import Path

import yaml

CANONICAL_HOST = "127.0.0.1"
CANONICAL_PORT = 3307
PORT_KEYS = frozenset({"port", "dolt.port", "server_port", "server-port"})
ENV_PORT_KEYS = frozenset({"GT_DOLT_PORT", "BEADS_DOLT_PORT", "BEADS_DOLT_SERVER_PORT"})
SKIP_PARTS = frozenset({".git", "node_modules"})


@dataclass(frozen=True)
class DoltFinding:
    path: str
    code: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return asdict(self)


def _yaml(path: Path) -> dict[object, object]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _port(value: object) -> int | None:
    try:
        return int(str(value))
    except ValueError:
        return None


def _config_findings(path: Path) -> list[DoltFinding]:
    try:
        payload = _yaml(path)
    except (OSError, yaml.YAMLError) as error:
        return [DoltFinding(str(path), "invalid-config", str(error))]
    found: list[DoltFinding] = []
    dolt = payload.get("dolt")
    if isinstance(dolt, dict) and dolt.get("shared-server") is True:
        found.append(DoltFinding(str(path), "shared-server", "standalone shared-server mode is prohibited"))
    values: list[object] = [payload[key] for key in PORT_KEYS if key in payload]
    if isinstance(dolt, dict):
        values.extend(dolt[key] for key in PORT_KEYS if key in dolt)
    for value in values:
        port = _port(value)
        if port != CANONICAL_PORT:
            found.append(DoltFinding(str(path), "noncanonical-port", f"configured port {value!r}; required {CANONICAL_PORT}"))
    return found


def _metadata_findings(path: Path) -> list[DoltFinding]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return [DoltFinding(str(path), "invalid-metadata", str(error))]
    mode = str(payload.get("dolt_mode", "server"))
    port = _port(payload.get("dolt_server_port"))
    host = str(payload.get("dolt_server_host", CANONICAL_HOST))
    found: list[DoltFinding] = []
    if mode != "server":
        found.append(DoltFinding(str(path), "noncanonical-mode", f"metadata mode {mode!r}; required 'server'"))
        return found
    if port != CANONICAL_PORT:
        found.append(DoltFinding(str(path), "noncanonical-port", f"metadata port {port!r}; required {CANONICAL_PORT}"))
    if host != CANONICAL_HOST:
        found.append(DoltFinding(str(path), "noncanonical-host", f"metadata host {host!r}; required {CANONICAL_HOST}"))
    return found


def _atomic_write(path: Path, content: str) -> None:
    temporary = path.with_name(f".{path.name}.agentsctl.{os.getpid()}")
    mode = stat.S_IMODE(path.stat().st_mode)
    try:
        temporary.write_text(content, encoding="utf-8")
        temporary.chmod(mode)
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def _rig_database(path: Path, town: Path, current: object) -> str:
    parts = list(path.relative_to(town).parts)
    if not parts:
        return str(current or "hq")
    if parts[0] == ".beads":
        return "hq"
    if parts[0] == "mayor":
        return str(current or "hq")
    if parts[0] == "deacon" and len(parts) > 3:
        return parts[3]
    return parts[0]


def repair(town: Path) -> list[Path]:
    """Converge every discovered Gas Town Beads client onto the sole endpoint."""
    changed: list[Path] = []
    for path in _managed_files(town, "config.yaml"):
        if path.parent.name != ".beads":
            continue
        original = path.read_text(encoding="utf-8")
        lines: list[str] = []
        for line in original.splitlines():
            if re.match(r"^\s*shared-server\s*:", line):
                continue
            if re.match(r"^\s*(?:dolt\.)?port\s*:", line):
                indent = line[: len(line) - len(line.lstrip())]
                key = "dolt.port" if line.lstrip().startswith("dolt.port") else "port"
                line = f'{indent}{key}: "{CANONICAL_PORT}"'
            lines.append(line)
        rendered = "\n".join(lines) + "\n"
        if rendered != original:
            _atomic_write(path, rendered)
            changed.append(path)
    for path in _managed_files(town, "metadata.json"):
        if path.parent.name != ".beads":
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            continue
        before = dict(payload)
        payload["backend"] = "dolt"
        payload["database"] = "dolt"
        payload["dolt_mode"] = "server"
        payload["dolt_server_host"] = CANONICAL_HOST
        payload["dolt_server_port"] = CANONICAL_PORT
        payload["dolt_database"] = _rig_database(path, town, payload.get("dolt_database"))
        if payload != before:
            _atomic_write(path, json.dumps(payload, indent=2, sort_keys=True) + "\n")
            changed.append(path)
    return sorted(changed)


def _managed_files(town: Path, name: str) -> list[Path]:
    if not town.is_dir():
        return []
    return sorted(path for path in town.rglob(name) if not (SKIP_PARTS & set(path.parts)))


def _process_findings(proc: Path) -> list[DoltFinding]:
    found: list[DoltFinding] = []
    if not proc.is_dir():
        return found
    listening_inodes: set[str] | None = None
    if proc == Path("/proc"):
        listening_inodes = set()
        for table in (proc / "net" / "tcp", proc / "net" / "tcp6"):
            try:
                rows = table.read_text(encoding="utf-8").splitlines()[1:]
            except OSError:
                continue
            for row in rows:
                fields = row.split()
                if len(fields) > 9 and fields[3] == "0A":
                    listening_inodes.add(fields[9])
    for command_file in proc.glob("[0-9]*/cmdline"):
        try:
            command = command_file.read_bytes().replace(b"\0", b" ").decode(errors="replace")
        except (OSError, PermissionError):
            continue
        if "dolt sql-server" not in command:
            continue
        if listening_inodes is not None:
            try:
                sockets = {
                    target[8:-1]
                    for fd in (command_file.parent / "fd").iterdir()
                    if (target := os.readlink(fd)).startswith("socket:[")
                }
            except (OSError, PermissionError):
                sockets = set()
            if not (sockets & listening_inodes):
                continue
        match = re.search(r"(?:^|\s)(?:-P\s+|--port(?:=|\s+))(\d+)(?:\s|$)", command)
        port = int(match.group(1)) if match else CANONICAL_PORT
        if port != CANONICAL_PORT:
            found.append(DoltFinding(str(command_file.parent), "noncanonical-listener", f"live dolt sql-server listens on {port}"))
    return found


def _binary_findings(home: Path) -> list[DoltFinding]:
    found: list[DoltFinding] = []
    root = home / ".local" / "share" / "mise" / "installs" / "github-dolt-hub-dolt"
    for binary in sorted(root.glob("*/bin/dolt")):
        try:
            header = binary.read_bytes()[:256]
        except OSError as error:
            found.append(DoltFinding(str(binary), "unreadable-binary", str(error)))
            continue
        if b"Machine invariant: the only Dolt SQL listener" not in header:
            found.append(DoltFinding(str(binary), "unguarded-binary", "Dolt can start an alternate listener"))
        if not binary.with_name("dolt.real").is_file():
            found.append(DoltFinding(str(binary), "missing-owned-binary", "guard has no physical dolt.real delegate"))
    return found


def audit(town: Path, *, environ: dict[str, str] | None = None, proc: Path = Path("/proc")) -> list[DoltFinding]:
    """Return every route that can select a noncanonical production endpoint."""
    found: list[DoltFinding] = []
    for path in _managed_files(town, "config.yaml"):
        if path.parent.name == ".beads":
            found.extend(_config_findings(path))
    for path in _managed_files(town, "metadata.json"):
        if path.parent.name == ".beads":
            found.extend(_metadata_findings(path))
    home = town.parent
    for path in (home / ".beads" / "config.yaml", home / ".agents" / ".beads" / "config.yaml"):
        if path.is_file():
            found.extend(_config_findings(path))
    agents_metadata = home / ".agents" / ".beads" / "metadata.json"
    if agents_metadata.is_file():
        found.extend(_metadata_findings(agents_metadata))
    found.extend(_binary_findings(home))
    env = dict(os.environ if environ is None else environ)
    if env.get("BEADS_DOLT_SHARED_SERVER", "").lower() in {"1", "true", "yes", "on"}:
        found.append(DoltFinding("environment", "shared-server", "BEADS_DOLT_SHARED_SERVER enables a prohibited server"))
    for key in sorted(ENV_PORT_KEYS):
        if key in env and _port(env[key]) != CANONICAL_PORT:
            found.append(DoltFinding("environment", "noncanonical-port", f"{key}={env[key]!r}; required {CANONICAL_PORT}"))
    found.extend(_process_findings(proc))
    return sorted(found, key=lambda item: (item.path, item.code, item.message))
