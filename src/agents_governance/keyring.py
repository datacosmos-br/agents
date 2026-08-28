"""Scoped GNOME Keyring bridge for direnv, agents, and user services."""

from __future__ import annotations

import argparse
import fnmatch
import getpass
import hmac
import json
import os
import re
import shlex
import subprocess
import sys
import time
import tomllib
from pathlib import Path
from typing import TypedDict

APP = "dev-environment"
CONFIG_ROOT = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
STATE_ROOT = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local/state"))
MANIFEST = CONFIG_ROOT / "environment.d" / "secrets" / "profiles.toml"
EVENTS = STATE_ROOT / "env-keyring" / "events.jsonl"
NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
PROFILE_RE = re.compile(r"^[a-z][a-z0-9-]{1,63}$")
EXPANDABLE_ROOTS = frozenset(
    {"HOME", "XDG_CONFIG_HOME", "XDG_CACHE_HOME", "XDG_STATE_HOME"}
)
_PROFILE_FIELDS = frozenset(
    {"aliases", "auto_load", "consumers", "roots", "shell_variables", "variables"}
)


class ProfileConfig(TypedDict):
    """Validated keyring profile consumed by every runtime surface."""

    variables: list[str]
    aliases: dict[str, str]
    shell_variables: list[str]
    roots: list[str]
    consumers: list[str]
    auto_load: bool


class KeyringError(RuntimeError):
    pass


def subprocess_error(
    operation: str, process: subprocess.CompletedProcess[str]
) -> KeyringError:
    """Preserve a subprocess exit and its non-secret diagnostic stderr."""
    detail = process.stderr.strip()
    suffix = f": {detail}" if detail else ""
    return KeyringError(f"{operation} failed (exit {process.returncode}){suffix}")


def event(action: str, profile: str, *, name: str = "", result: str) -> None:
    EVENTS.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    payload = {
        "timestamp": int(time.time()),
        "action": action,
        "profile": profile,
        "name": name,
        "result": result,
    }
    descriptor = os.open(EVENTS, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600)
    with os.fdopen(descriptor, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True) + "\n")


def _string_list(
    raw: dict[str, object], field: str, profile: str, *, required: bool = False
) -> list[str]:
    value = raw.get(field, [])
    if (
        not isinstance(value, list)
        or (required and not value)
        or any(not isinstance(item, str) or not item for item in value)
        or len(set(value)) != len(value)
    ):
        raise KeyringError(f"invalid {field} for profile: {profile}")
    return value


def _parse_profile(name: str, raw: object) -> ProfileConfig:
    if not PROFILE_RE.fullmatch(name) or not isinstance(raw, dict):
        raise KeyringError(f"invalid profile: {name}")
    unknown = set(raw) - _PROFILE_FIELDS
    if unknown:
        raise KeyringError(f"unknown fields for profile {name}: {sorted(unknown)}")
    variables = _string_list(raw, "variables", name, required=True)
    if any(NAME_RE.fullmatch(item) is None for item in variables):
        raise KeyringError(f"invalid variables for profile: {name}")
    raw_aliases = raw.get("aliases", {})
    if not isinstance(raw_aliases, dict):
        raise KeyringError(f"invalid aliases for profile: {name}")
    aliases: dict[str, str] = {}
    for alias, source in raw_aliases.items():
        if (
            not isinstance(alias, str)
            or NAME_RE.fullmatch(alias) is None
            or not isinstance(source, str)
            or source not in variables
            or alias in variables
        ):
            raise KeyringError(f"invalid aliases for profile: {name}")
        aliases[alias] = source
    shell_variables = _string_list(raw, "shell_variables", name)
    declared = {*variables, *aliases}
    if any(item not in declared for item in shell_variables):
        raise KeyringError(f"invalid shell_variables for profile: {name}")
    auto_load = raw.get("auto_load", False)
    if not isinstance(auto_load, bool):
        raise KeyringError(f"invalid auto_load for profile: {name}")
    return ProfileConfig(
        variables=variables,
        aliases=aliases,
        shell_variables=shell_variables,
        roots=_string_list(raw, "roots", name),
        consumers=_string_list(raw, "consumers", name),
        auto_load=auto_load,
    )


def manifest() -> dict[str, ProfileConfig]:
    try:
        data = tomllib.loads(MANIFEST.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as error:
        raise KeyringError(f"manifest unavailable: {error}") from error
    profiles = data.get("profiles")
    if data.get("version") != 1 or not isinstance(profiles, dict):
        raise KeyringError("invalid manifest version or profiles")
    result: dict[str, ProfileConfig] = {}
    for name, raw in profiles.items():
        if not isinstance(name, str):
            raise KeyringError("profile names must be strings")
        result[name] = _parse_profile(name, raw)
    return result


def profile_config(name: str) -> ProfileConfig:
    if not PROFILE_RE.fullmatch(name):
        raise KeyringError("invalid profile name")
    config = manifest().get(name)
    if config is None:
        raise KeyringError(f"unknown profile: {name}")
    return config


def expand_root(raw_root: str) -> Path:
    """Expand the small, declared path vocabulary accepted by the manifest."""
    expanded = raw_root
    for match in re.finditer(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}", raw_root):
        name = match.group(1)
        if name not in EXPANDABLE_ROOTS:
            raise KeyringError(f"unsupported root variable: {name}")
        value = os.environ.get(name)
        if not value:
            raise KeyringError(f"required root variable is unset: {name}")
        expanded = expanded.replace(match.group(0), value)
    if "$" in expanded:
        raise KeyringError("unresolved root variable")
    result = Path(expanded).expanduser()
    if not result.is_absolute():
        raise KeyringError("profile roots must be absolute")
    return result


def auto_profile(directory: str | None) -> tuple[str, ProfileConfig] | None:
    current = Path(directory or os.getcwd()).resolve(strict=True)
    candidates: list[tuple[int, str, ProfileConfig]] = []
    for name, config in manifest().items():
        if not config["auto_load"]:
            continue
        for raw_root in config["roots"]:
            root = expand_root(raw_root)
            if not root.exists():
                continue
            resolved = root.resolve(strict=True)
            if within(current, resolved):
                candidates.append((len(resolved.parts), name, config))
    if not candidates:
        return None
    depth = max(item[0] for item in candidates)
    winners = {
        (name, id(config)): (name, config)
        for item_depth, name, config in candidates
        if item_depth == depth
    }
    if len(winners) != 1:
        raise KeyringError("ambiguous automatic keyring profile")
    return next(iter(winners.values()))


def within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def authorize_directory(config: ProfileConfig, directory: str | None) -> None:
    current = Path(directory or os.getcwd()).resolve(strict=True)
    if not any(
        root.exists() and within(current, root.resolve(strict=True))
        for root in (expand_root(item) for item in config["roots"])
    ):
        raise KeyringError("directory is not authorized for this profile")


def authorize_consumer(config: ProfileConfig, consumer: str) -> None:
    if not any(
        fnmatch.fnmatchcase(consumer, pattern) for pattern in config["consumers"]
    ):
        raise KeyringError("consumer is not authorized for this profile")


def lookup(profile: str, name: str) -> str:
    if not os.environ.get("DBUS_SESSION_BUS_ADDRESS"):
        raise KeyringError("GNOME Keyring unavailable: session D-Bus is not configured")
    process = subprocess.run(
        ["secret-tool", "lookup", "application", APP, "profile", profile, "name", name],
        check=False,
        capture_output=True,
        text=True,
        timeout=15,
    )
    if process.returncode == 1 and not process.stderr.strip():
        raise KeyringError(f"missing secret: {name}")
    if process.returncode != 0:
        raise subprocess_error("secret-tool lookup", process)
    if not process.stdout:
        raise KeyringError(f"missing secret: {name}")
    return process.stdout.rstrip("\n")


def fetch_all(profile: str, config: ProfileConfig) -> dict[str, str]:
    result: dict[str, str] = {}
    for name in config["variables"]:
        result[str(name)] = lookup(profile, str(name))
    for alias, source in config["aliases"].items():
        result[str(alias)] = result[str(source)]
    return result


def fetch_shell(profile: str, config: ProfileConfig) -> dict[str, str]:
    """Fetch only values explicitly authorized for ambient project shells."""
    aliases = config["aliases"]
    result: dict[str, str] = {}
    canonical: dict[str, str] = {}
    for raw_name in config["shell_variables"]:
        name = str(raw_name)
        source = str(aliases.get(name, name))
        if source not in canonical:
            canonical[source] = lookup(profile, source)
        result[name] = canonical[source]
    return result


def declared_export_names(config: ProfileConfig) -> set[str]:
    """Return every canonical and aliased environment export name."""
    return {
        *config["variables"],
        *config["aliases"],
    }


def store(profile: str, name: str, from_stdin: bool) -> int:
    config = profile_config(profile)
    if name not in config["variables"]:
        raise KeyringError("variable is not declared by the profile")
    value = sys.stdin.read() if from_stdin else getpass.getpass(f"{profile}/{name}: ")
    value = value.rstrip("\n") if from_stdin else value
    if not value:
        raise KeyringError("refusing to store an empty secret")
    process = subprocess.run(
        [
            "secret-tool",
            "store",
            f"--label={APP}: {profile}/{name}",
            "application",
            APP,
            "profile",
            profile,
            "name",
            name,
        ],
        input=value,
        text=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        check=False,
        timeout=30,
    )
    if process.returncode != 0:
        event("store", profile, name=name, result="failed")
        raise subprocess_error("secret-tool store", process)
    if not hmac.compare_digest(lookup(profile, name), value):
        event("store", profile, name=name, result="failed")
        raise KeyringError("keyring verification failed")
    event("store", profile, name=name, result="ok")
    return 0


def shell_exports(profile: str, directory: str | None, shell: str) -> int:
    config = profile_config(profile)
    authorize_directory(config, directory)
    secrets = fetch_shell(profile, config)
    for name, value in secrets.items():
        if shell == "fish":
            print(f"set -gx {name} {shlex.quote(value)}")
        else:
            print(f"export {name}={shlex.quote(value)}")
    event("shell", profile, result="ok")
    return 0


def auto_shell_exports(directory: str | None, shell: str) -> int:
    selected = auto_profile(directory)
    if selected is None:
        return 0
    profile, config = selected
    secrets = fetch_shell(profile, config)
    secrets["ENV_KEYRING_PROFILE"] = profile
    for name, value in secrets.items():
        if shell == "fish":
            print(f"set -gx {name} {shlex.quote(value)}")
        else:
            print(f"export {name}={shlex.quote(value)}")
    event("auto-shell", profile, result="ok")
    return 0


def check(profile: str, directory: str | None, consumer: str | None) -> int:
    config = profile_config(profile)
    if consumer:
        authorize_consumer(config, consumer)
    else:
        authorize_directory(config, directory)
    fetch_all(profile, config)
    event("check", profile, result="ok")
    print(f"profile={profile} status=ready variables={len(config['variables'])}")
    return 0


def credential(consumer: str, name: str) -> int:
    """Emit one credential for an explicitly authorized non-shell consumer."""
    matches: list[tuple[str, ProfileConfig]] = []
    for profile in manifest():
        configured = profile_config(profile)
        variables = configured["variables"]
        if name in variables:
            try:
                authorize_consumer(configured, consumer)
            except KeyringError:
                continue
            matches.append((profile, configured))
    if len(matches) != 1:
        raise KeyringError("credential consumer mapping must resolve exactly once")
    profile, _config = matches[0]
    print(lookup(profile, name))
    event("credential", profile, name=name, result="ok")
    return 0


def validate_manifest() -> int:
    """Validate profiles, portable roots, aliases, and export boundaries."""
    profiles = manifest()
    for profile in sorted(profiles):
        config = profile_config(profile)
        roots = config["roots"]
        if not roots:
            raise KeyringError(f"profile has no roots: {profile}")
        for root in roots:
            expand_root(root)
    print(f"profiles={len(profiles)} status=valid")
    return 0


def execute(profile: str, consumer: str, command: list[str]) -> int:
    config = profile_config(profile)
    authorize_consumer(config, consumer)
    secrets = fetch_all(profile, config)
    environment = os.environ.copy()
    for item in manifest().values():
        for name in declared_export_names(item):
            environment.pop(name, None)
    environment.update(secrets)
    event("exec", profile, result="dispatch")
    os.execvpe(command[0], command, environment)
    return 70


def execute_auto(directory: str | None, consumer: str, command: list[str]) -> int:
    selected = auto_profile(directory)
    if selected is None:
        raise KeyringError("no automatic keyring profile for directory")
    profile, config = selected
    authorize_consumer(config, consumer)
    secrets = fetch_all(profile, config)
    environment = os.environ.copy()
    for item in manifest().values():
        for name in declared_export_names(item):
            environment.pop(name, None)
    environment.update(secrets)
    environment["ENV_KEYRING_PROFILE"] = profile
    event("auto-exec", profile, result="dispatch")
    os.execvpe(command[0], command, environment)
    return 70


def remove(profile: str, name: str, confirmed: bool) -> int:
    config = profile_config(profile)
    if not confirmed or name not in declared_export_names(config):
        raise KeyringError("explicit --yes and a declared name are required")
    process = subprocess.run(
        ["secret-tool", "clear", "application", APP, "profile", profile, "name", name],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
        timeout=15,
    )
    event(
        "remove",
        profile,
        name=name,
        result="ok" if process.returncode == 0 else "failed",
    )
    if process.returncode != 0:
        print(
            f"env-keyring: {subprocess_error('secret-tool clear', process)}",
            file=sys.stderr,
        )
    return process.returncode


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="env-keyring")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("validate")
    store_parser = commands.add_parser("store")
    store_parser.add_argument("--profile", required=True)
    store_parser.add_argument("--name", required=True)
    store_parser.add_argument("--stdin", action="store_true")
    shell_parser = commands.add_parser("shell")
    shell_parser.add_argument("--profile", required=True)
    shell_parser.add_argument("--directory")
    shell_parser.add_argument(
        "--shell", choices=("bash", "zsh", "fish"), default="bash"
    )
    auto_shell_parser = commands.add_parser("auto-shell")
    auto_shell_parser.add_argument("--directory")
    auto_shell_parser.add_argument(
        "--shell", choices=("bash", "zsh", "fish"), default="bash"
    )
    check_parser = commands.add_parser("check")
    check_parser.add_argument("--profile", required=True)
    check_parser.add_argument("--directory")
    check_parser.add_argument("--consumer")
    credential_parser = commands.add_parser("credential")
    credential_parser.add_argument("--consumer", required=True)
    credential_parser.add_argument("--name", required=True)
    exec_parser = commands.add_parser("exec")
    exec_parser.add_argument("--profile", required=True)
    exec_parser.add_argument("--consumer", required=True)
    exec_parser.add_argument("argv", nargs=argparse.REMAINDER)
    auto_exec_parser = commands.add_parser("auto-exec")
    auto_exec_parser.add_argument("--directory")
    auto_exec_parser.add_argument("--consumer", required=True)
    auto_exec_parser.add_argument("argv", nargs=argparse.REMAINDER)
    remove_parser = commands.add_parser("remove")
    remove_parser.add_argument("--profile", required=True)
    remove_parser.add_argument("--name", required=True)
    remove_parser.add_argument("--yes", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.command == "validate":
            return validate_manifest()
        if args.command == "store":
            return store(args.profile, args.name, args.stdin)
        if args.command == "shell":
            return shell_exports(args.profile, args.directory, args.shell)
        if args.command == "auto-shell":
            return auto_shell_exports(args.directory, args.shell)
        if args.command == "check":
            return check(args.profile, args.directory, args.consumer)
        if args.command == "credential":
            return credential(args.consumer, args.name)
        if args.command == "exec":
            command = list(args.argv)
            if command and command[0] == "--":
                command.pop(0)
            if not command:
                raise KeyringError("exec requires a command after --")
            return execute(args.profile, args.consumer, command)
        if args.command == "auto-exec":
            command = list(args.argv)
            if command and command[0] == "--":
                command.pop(0)
            if not command:
                raise KeyringError("auto-exec requires a command after --")
            return execute_auto(args.directory, args.consumer, command)
        if args.command == "remove":
            return remove(args.profile, args.name, args.yes)
    except (KeyringError, OSError, subprocess.SubprocessError) as error:
        profile = getattr(args, "profile", "unknown")
        event(args.command, profile, result="failed")
        print(f"env-keyring: {error}", file=sys.stderr)
        return 78
    return 70


if __name__ == "__main__":
    raise SystemExit(main())
