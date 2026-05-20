#!/usr/bin/env python3
"""Prepare and launch a Cherry Studio testable MCP package locally."""

from __future__ import annotations

import argparse
import json
import os
import re
import socket
import subprocess
import sys
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from venv import EnvBuilder


PROXY_KEYS = [
    "ALL_PROXY",
    "all_proxy",
    "HTTP_PROXY",
    "http_proxy",
    "HTTPS_PROXY",
    "https_proxy",
]


def slugify(value: str) -> str:
    cleaned = value.strip().lower()
    cleaned = re.sub(r"[^a-z0-9]+", "_", cleaned)
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")
    return cleaned or "mcp_service"


def remove_proxy_env(env: dict[str, str]) -> dict[str, str]:
    cleaned = env.copy()
    for key in PROXY_KEYS:
        cleaned.pop(key, None)
    return cleaned


def run_checked(
    cmd: list[str],
    *,
    cwd: Path,
    env: dict[str, str],
    retry_without_proxy: bool = False,
) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            cmd,
            cwd=cwd,
            env=env,
            check=True,
            text=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError as exc:
        if retry_without_proxy and any(key in env for key in PROXY_KEYS):
            clean_env = remove_proxy_env(env)
            try:
                return subprocess.run(
                    cmd,
                    cwd=cwd,
                    env=clean_env,
                    check=True,
                    text=True,
                    capture_output=True,
                )
            except subprocess.CalledProcessError as retry_exc:
                raise SystemExit(format_command_error(cmd, retry_exc)) from retry_exc
        raise SystemExit(format_command_error(cmd, exc)) from exc


def format_command_error(cmd: list[str], exc: subprocess.CalledProcessError) -> str:
    joined = " ".join(cmd)
    stdout = exc.stdout.strip()
    stderr = exc.stderr.strip()
    details = stderr or stdout or "no output captured"
    return f"Command failed: {joined}\n{details}"


def find_open_port(host: str, preferred_port: int) -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.bind((host, preferred_port))
            return preferred_port
        except OSError:
            pass

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((host, 0))
        return int(sock.getsockname()[1])


def infer_package_name(root: Path) -> str:
    candidates = []
    for path in root.iterdir():
        if not path.is_dir() or path.name in {"business", "deploy", ".venv", "logs", "__pycache__"}:
            continue
        if (
            (path / "pyproject.toml").exists()
            and (path / "run_mcp_server.py").exists()
            and (path / path.name / "server.py").exists()
        ):
            candidates.append(path.name)

    if len(candidates) == 1:
        return candidates[0]
    if not candidates:
        raise SystemExit("Could not infer package name from the package root.")
    raise SystemExit(f"Multiple package candidates found: {', '.join(sorted(candidates))}")


def write_local_env(root: Path, host: str, port: int) -> None:
    env_text = "\n".join(
        [
            f"MCP_HOST={host}",
            f"MCP_PORT={port}",
            "MCP_TRANSPORT=sse",
            "",
        ]
    )
    (root / ".env").write_text(env_text, encoding="utf-8")


def ensure_venv(root: Path) -> Path:
    venv_root = root / ".venv"
    if not venv_root.exists():
        EnvBuilder(with_pip=True).create(venv_root)
    python_path = venv_root / "bin" / "python"
    if not python_path.exists():
        raise SystemExit(f"Virtualenv python not found: {python_path}")
    return python_path


def bootstrap_package(
    *,
    script_dir: Path,
    root: Path,
    business_name: str,
    package_name: str,
    project_name: str | None,
    domain: str,
    force: bool,
) -> None:
    base_env = os.environ.copy()
    init_cmd = [sys.executable, str(script_dir / "init_mcp_package.py"), "--output", str(root)]
    if force:
        init_cmd.append("--force")
    run_checked(init_cmd, cwd=script_dir, env=base_env)

    render_cmd = [
        sys.executable,
        str(script_dir / "render_package.py"),
        "--root",
        str(root),
        "--business-name",
        business_name,
        "--package-name",
        package_name,
        "--domain",
        domain,
    ]
    if project_name:
        render_cmd.extend(["--project-name", project_name])
    run_checked(render_cmd, cwd=script_dir, env=base_env)


def validate_package(script_dir: Path, root: Path, package_name: str) -> None:
    run_checked(
        [
            sys.executable,
            str(script_dir / "validate_package.py"),
            "--root",
            str(root),
            "--package-name",
            package_name,
        ],
        cwd=script_dir,
        env=os.environ.copy(),
    )


def install_dependencies(root: Path, package_name: str) -> Path:
    python_path = ensure_venv(root)
    env = os.environ.copy()
    run_checked(
        [str(python_path), "-m", "pip", "install", "--upgrade", "pip"],
        cwd=root,
        env=env,
        retry_without_proxy=True,
    )
    run_checked(
        [str(python_path), "-m", "pip", "install", "-e", str(root / package_name)],
        cwd=root,
        env=env,
        retry_without_proxy=True,
    )
    return python_path


def launch_server(root: Path, python_path: Path, package_name: str, host: str, port: int) -> tuple[subprocess.Popen[bytes], Path]:
    logs_dir = root / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_path = logs_dir / "local-test.log"
    env = os.environ.copy()
    env.update(
        {
            "MCP_HOST": host,
            "MCP_PORT": str(port),
            "MCP_TRANSPORT": "sse",
        }
    )

    log_handle = log_path.open("ab")
    process = subprocess.Popen(
        [str(python_path), str(root / package_name / "run_mcp_server.py")],
        cwd=root,
        env=env,
        stdout=log_handle,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    log_handle.close()
    return process, log_path


def probe_sse(url: str, process: subprocess.Popen[bytes], log_path: Path, timeout_seconds: int) -> None:
    deadline = time.time() + timeout_seconds
    request = Request(url, headers={"Accept": "text/event-stream"})
    last_error = "service did not respond"

    while time.time() < deadline:
        if process.poll() is not None:
            try:
                log_tail = log_path.read_text(encoding="utf-8")[-2000:]
            except FileNotFoundError:
                log_tail = "log file not found"
            raise SystemExit(
                "MCP service exited before becoming healthy.\n"
                f"Log tail:\n{log_tail}"
            )

        try:
            with urlopen(request, timeout=2) as response:
                content_type = response.headers.get("content-type", "")
                if response.status == 200 and "text/event-stream" in content_type:
                    return
                last_error = f"unexpected response: {response.status} {content_type}"
        except HTTPError as exc:
            last_error = f"http error: {exc.code}"
        except URLError as exc:
            last_error = f"url error: {exc.reason}"
        except TimeoutError:
            last_error = "timed out waiting for sse response"
        time.sleep(1)

    raise SystemExit(f"SSE health check failed for {url}: {last_error}")


def write_runtime_info(root: Path, host: str, port: int, process: subprocess.Popen[bytes], log_path: Path) -> Path:
    runtime_path = root / "local_test_runtime.json"
    payload = {
        "transport": "SSE",
        "url": f"http://{host}:{port}/sse",
        "host": host,
        "port": port,
        "pid": process.pid,
        "log_path": str(log_path),
    }
    runtime_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return runtime_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare and start a Cherry Studio testable local MCP package.")
    parser.add_argument("--root", required=True, help="Package root directory.")
    parser.add_argument("--package-name", help="Rendered python package name.")
    parser.add_argument("--business-name", help="Required when --bootstrap is used.")
    parser.add_argument("--project-name", help="Optional project name for bootstrap mode.")
    parser.add_argument("--domain", default="your-domain.example.com", help="Domain placeholder for bootstrap mode.")
    parser.add_argument("--host", default="127.0.0.1", help="Host for local testing.")
    parser.add_argument("--preferred-port", type=int, default=8000, help="Preferred local port.")
    parser.add_argument("--timeout-seconds", type=int, default=20, help="Health check timeout.")
    parser.add_argument("--bootstrap", action="store_true", help="Initialize and render a fresh scaffold before testing.")
    parser.add_argument("--force", action="store_true", help="Allow bootstrap into a non-empty directory.")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    script_dir = Path(__file__).resolve().parent

    if args.bootstrap:
        if not args.business_name:
            raise SystemExit("--business-name is required when --bootstrap is set.")
        package_name = args.package_name or slugify(args.business_name)
        bootstrap_package(
            script_dir=script_dir,
            root=root,
            business_name=args.business_name,
            package_name=package_name,
            project_name=args.project_name,
            domain=args.domain,
            force=args.force,
        )
    else:
        if not root.exists():
            raise SystemExit(f"Package root does not exist: {root}")
        package_name = args.package_name or infer_package_name(root)

    validate_package(script_dir, root, package_name)

    port = find_open_port(args.host, args.preferred_port)
    write_local_env(root, args.host, port)
    python_path = install_dependencies(root, package_name)
    process, log_path = launch_server(root, python_path, package_name, args.host, port)
    probe_sse(f"http://{args.host}:{port}/sse", process, log_path, args.timeout_seconds)
    runtime_path = write_runtime_info(root, args.host, port, process, log_path)

    print("transport=SSE")
    print(f"url=http://{args.host}:{port}/sse")
    print(f"runtime={runtime_path}")
    print(f"log={log_path}")


if __name__ == "__main__":
    main()
