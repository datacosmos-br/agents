#!/usr/bin/env python3
"""Run local servers and a command with argv execution and guaranteed cleanup.

Each --server accepts a quoted argv command, optionally prefixed with
``cd DIRECTORY &&``. No shell expansion, pipeline or command substitution runs.
"""

# Copyright (c) 2026 agents-governance contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import asyncio
import getopt
import os
import shlex
import shutil
import signal
import socket
import sys
import time
from pathlib import Path

DEFAULT_TIMEOUT = 30
POLL_INTERVAL = 0.5
CONNECT_TIMEOUT = 1
SHUTDOWN_TIMEOUT = 5
DIRECTORY_PREFIX_LENGTH = 3
USAGE = (
    "with_server.py --server CMD --port PORT [--server CMD --port PORT ...] "
    "[--timeout SECONDS] -- COMMAND [ARG ...]"
)


def parse_args(argv: list[str]) -> tuple[list[str], list[int], int, list[str]]:
    """Parse repeated server/port declarations and the untouched command argv.

    Returns:
        Server commands, corresponding ports, readiness timeout and command argv.

    Raises:
        ValueError: If the server declarations, timeout or command are invalid.

    """
    options, command = getopt.getopt(argv, "", ["server=", "port=", "timeout=", "help"])
    servers: list[str] = []
    ports: list[int] = []
    timeout = DEFAULT_TIMEOUT
    for option, value in options:
        if option == "--help":
            sys.stdout.write(f"{USAGE}\n")
            sys.exit(0)
        if option == "--server":
            servers.append(value)
        elif option == "--port":
            ports.append(int(value))
        else:
            timeout = int(value)
    if not servers or len(servers) != len(ports) or timeout <= 0 or not command:
        message = "supply one port per server, a positive timeout and a command"
        raise ValueError(message)
    return servers, ports, timeout, command


def server_command(command: str) -> tuple[tuple[str, ...], Path]:
    """Parse server argv and its optional leading working-directory declaration.

    Returns:
        The server argv and its absolute working directory.

    Raises:
        ValueError: If the server argv or directory declaration is empty.
        NotADirectoryError: If the working directory does not exist.

    """
    argv = shlex.split(command)
    cwd = Path.cwd()
    if argv and argv[0] == "cd":
        if len(argv) <= DIRECTORY_PREFIX_LENGTH or argv[2] != "&&":
            message = "server directory syntax is: cd DIRECTORY && COMMAND [ARG ...]"
            raise ValueError(message)
        cwd = (cwd / Path(argv[1]).expanduser()).resolve()
        argv = argv[DIRECTORY_PREFIX_LENGTH:]
    if not argv:
        message = "server command must contain an executable"
        raise ValueError(message)
    if not cwd.is_dir():
        raise NotADirectoryError(str(cwd))
    return tuple(argv), cwd


def resolve_executable(command: str, cwd: Path) -> str:
    """Resolve an executable without changing the caller's working directory.

    Returns:
        The absolute executable path, preserving interpreter symlinks.

    Raises:
        FileNotFoundError: If the requested executable is unavailable.

    """
    executable = (
        shutil.which(str(cwd / command)) if os.sep in command else shutil.which(command)
    )
    if executable is None:
        raise FileNotFoundError(command)
    return str(Path(executable).absolute())


async def start_process(argv: tuple[str, ...], cwd: Path) -> asyncio.subprocess.Process:
    """Start argv directly, preserving cwd, argument boundaries and streams.

    Returns:
        The native asyncio process handle.

    """
    executable = await asyncio.to_thread(resolve_executable, argv[0], cwd)
    return await asyncio.create_subprocess_exec(
        executable,
        *argv[1:],
        cwd=cwd,
        start_new_session=os.name == "posix",
    )


def is_server_ready(port: int, timeout: int = DEFAULT_TIMEOUT) -> bool:
    """Wait until a local port accepts connections within the readiness deadline.

    Returns:
        Whether a connection succeeded before the monotonic deadline.

    """
    deadline = time.monotonic() + timeout
    while (remaining := deadline - time.monotonic()) > 0:
        try:
            with socket.create_connection(
                ("localhost", port), timeout=min(CONNECT_TIMEOUT, remaining)
            ):
                return True
        except OSError:
            time.sleep(min(POLL_INTERVAL, max(0, deadline - time.monotonic())))
    return False


def signal_process(process: asyncio.subprocess.Process, signum: signal.Signals) -> None:
    """Signal the owned POSIX process group or its direct non-POSIX child."""
    try:
        if os.name == "posix":
            os.killpg(process.pid, signum)
        elif process.returncode is None:
            process.send_signal(signum)
    except ProcessLookupError:
        # The owned process group can finish between its state check and signal.
        return


async def stop_process(process: asyncio.subprocess.Process) -> None:
    """Terminate an owned server, reap it, and remove surviving descendants."""
    signal_process(process, signal.SIGTERM)
    try:
        await asyncio.wait_for(process.wait(), timeout=SHUTDOWN_TIMEOUT)
    except TimeoutError:
        signal_process(process, signal.SIGKILL)
        await process.wait()
    if os.name == "posix":
        signal_process(process, signal.SIGKILL)


TERMINATION_SIGNALS = (signal.SIGTERM, signal.SIGINT, signal.SIGHUP)


async def run(
    servers: list[str],
    ports: list[int],
    readiness_seconds: int,
    command: list[str],
    received: list[signal.Signals],
) -> int:
    """Run the trailing argv after every server becomes ready.

    A termination signal cancels the run so every owned process group is
    stopped before the helper exits; ``received`` records that signal.

    Returns:
        The trailing command's exact native return code.

    Raises:
        RuntimeError: If a server fails to become ready within its deadline.

    """
    processes: list[asyncio.subprocess.Process] = []
    if os.name == "posix":
        loop = asyncio.get_running_loop()
        task = asyncio.current_task()

        def cancel_on(signum: signal.Signals) -> None:
            received.append(signum)
            if task is not None:
                task.cancel()

        for signum in TERMINATION_SIGNALS:
            loop.add_signal_handler(signum, cancel_on, signum)
    try:
        for server, port in zip(servers, ports, strict=True):
            argv, cwd = server_command(server)
            process = await start_process(argv, cwd)
            processes.append(process)
            if not await asyncio.to_thread(is_server_ready, port, readiness_seconds):
                message = (
                    f"Server failed to start on port {port} within {readiness_seconds}s"
                )
                raise RuntimeError(message)
        cwd = await asyncio.to_thread(Path.cwd)
        trailing_process = await start_process(tuple(command), cwd)
        processes.append(trailing_process)
        return await trailing_process.wait()
    finally:
        for process in reversed(processes):
            await stop_process(process)


def main() -> None:
    """Parse the helper CLI and propagate the trailing command's return code.

    After a termination signal has stopped every owned process group, the
    same signal is re-raised with its default action so the caller observes
    the native termination status.

    Raises:
        asyncio.CancelledError: If the run was cancelled without a signal.

    """
    received: list[signal.Signals] = []
    try:
        code = asyncio.run(run(*parse_args(sys.argv[1:]), received))
    except asyncio.CancelledError:
        if not received:
            raise
        signal.signal(received[0], signal.SIG_DFL)
        os.kill(os.getpid(), received[0])
        raise
    sys.exit(code)


if __name__ == "__main__":
    main()
