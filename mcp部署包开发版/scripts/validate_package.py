#!/usr/bin/env python3
"""Basic validator for generated MCP deployment packages."""

from __future__ import annotations

import argparse
from pathlib import Path


EXPECTED = [
    ".env.example",
    "README_DEPLOY.md",
    "start.sh",
    "business/README.md",
    "deploy/nginx/mcp.conf",
    "deploy/systemd/mcp.service",
]


def check_exists(root: Path, paths: list[str]) -> list[str]:
    missing: list[str] = []
    for relative in paths:
        if not (root / relative).exists():
            missing.append(relative)
    return missing


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate a generated MCP deployment package.")
    parser.add_argument("--root", required=True, help="Package root directory.")
    parser.add_argument("--package-name", help="Rendered python package name. If omitted, validator accepts any single top-level package dir.")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    missing = check_exists(root, EXPECTED)

    package_name = args.package_name
    if package_name:
        package_expected = [
            f"{package_name}/pyproject.toml",
            f"{package_name}/run_mcp_server.py",
            f"{package_name}/{package_name}/server.py",
        ]
        missing.extend(check_exists(root, package_expected))
    else:
        candidates = [
            path.name
            for path in root.iterdir()
            if path.is_dir() and path.name not in {"business", "deploy", ".venv", "__pycache__"}
        ]
        valid = False
        for candidate in candidates:
            if (
                (root / candidate / "pyproject.toml").exists()
                and (root / candidate / "run_mcp_server.py").exists()
                and (root / candidate / candidate / "server.py").exists()
            ):
                valid = True
                break
        if not valid:
            missing.append("<package_dir>/pyproject.toml + run_mcp_server.py + inner server.py")

    if missing:
        print("Missing files:")
        for item in missing:
            print(f"- {item}")
        raise SystemExit(1)

    print("Validation passed.")


if __name__ == "__main__":
    main()
