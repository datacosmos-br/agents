"""Exercise the distributed webapp server helper through its real CLI."""

from __future__ import annotations

import asyncio
import shlex
import socket
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import IsolatedAsyncioTestCase

HELPER = (
    Path(__file__).resolve().parents[1]
    / "skills/tool/webapp-test/scripts/with_server.py"
)


def free_port() -> int:
    """Return an available loopback TCP port for a real test server."""
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        return int(listener.getsockname()[1])


class TestWebappServer(IsolatedAsyncioTestCase):
    """Validate argv, cwd, readiness, return codes and cleanup without mocks."""

    async def test_multiple_servers_preserve_argv_cwd_and_exit(self) -> None:
        """Reach both real servers and preserve shell metacharacters as data."""
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            directory = root / "server with spaces"
            directory.mkdir()
            (directory / "index.html").write_text("server-ready", encoding="utf-8")
            ports = (free_port(), free_port())
            arguments: list[str] = []
            for port in ports:
                server = shlex.join(
                    (
                        sys.executable,
                        "-m",
                        "http.server",
                        str(port),
                        "--bind",
                        "127.0.0.1",
                    )
                )
                arguments.extend(
                    (
                        "--server",
                        f"cd {shlex.quote(str(directory))} && {server}",
                        "--port",
                        str(port),
                    )
                )
            literal = f"$(touch {root / 'must-not-exist'}) ; literal argument"
            command = (
                "import pathlib,sys,urllib.request; "
                "assert pathlib.Path.cwd() == pathlib.Path(sys.argv[1]); "
                "assert sys.argv[2].startswith('$(touch '); "
                "assert all(urllib.request.urlopen('http://127.0.0.1:'+port)"
                ".read() == b'server-ready' for port in sys.argv[3:]); "
                "raise SystemExit(7)"
            )
            process = await asyncio.create_subprocess_exec(
                sys.executable,
                str(HELPER),
                *arguments,
                "--",
                sys.executable,
                "-c",
                command,
                str(root),
                literal,
                *(str(port) for port in ports),
                cwd=root,
            )
            self.assertEqual(await asyncio.wait_for(process.wait(), 15), 7)
            self.assertFalse((root / "must-not-exist").exists())
            for port in ports:
                with self.assertRaises(OSError):
                    socket.create_connection(("127.0.0.1", port), timeout=1)

    async def test_readiness_failure_cleans_up_server(self) -> None:
        """A timeout remains a failure and reaps the owned sleeping server."""
        with TemporaryDirectory() as temporary:
            pid_path = Path(temporary) / "server.pid"
            server = shlex.join(
                (
                    sys.executable,
                    "-c",
                    (
                        "import os,pathlib,sys,time; "
                        "pathlib.Path(sys.argv[1]).write_text(str(os.getpid())); "
                        "time.sleep(60)"
                    ),
                    str(pid_path),
                )
            )
            process = await asyncio.create_subprocess_exec(
                sys.executable,
                str(HELPER),
                "--server",
                server,
                "--port",
                str(free_port()),
                "--timeout",
                "1",
                "--",
                sys.executable,
                "-c",
                "raise SystemExit(0)",
            )
            self.assertNotEqual(await asyncio.wait_for(process.wait(), 10), 0)
            self.assertTrue(pid_path.is_file())
            self.assertFalse(Path(f"/proc/{pid_path.read_text()}").exists())
