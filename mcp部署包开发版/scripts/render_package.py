#!/usr/bin/env python3
"""Render a generated MCP package scaffold with business-specific names."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


def slugify(value: str) -> str:
    cleaned = value.strip().lower()
    cleaned = re.sub(r"[^a-z0-9]+", "_", cleaned)
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")
    return cleaned or "mcp_service"


def replace_in_file(path: Path, replacements: dict[str, str]) -> None:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return
    for old, new in replacements.items():
        text = text.replace(old, new)
    path.write_text(text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Render MCP package scaffold placeholders.")
    parser.add_argument("--root", required=True, help="Generated package root directory.")
    parser.add_argument("--business-name", required=True, help="Human-readable business name.")
    parser.add_argument("--package-name", help="Python package name; defaults to slugified business name.")
    parser.add_argument("--project-name", help="Python project name; defaults to package name with dashes.")
    parser.add_argument("--domain", default="your-domain.example.com", help="Nginx server_name placeholder.")
    parser.add_argument("--service-description", help="systemd service description.")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    package_name = args.package_name or slugify(args.business_name)
    project_name = args.project_name or package_name.replace("_", "-")
    service_description = args.service_description or f"{args.business_name} MCP Service"

    old_outer = root / "package_name"
    old_inner = old_outer / "package_name"
    new_outer = root / package_name
    rendered_outer = root / package_name
    rendered_inner = rendered_outer / package_name

    if old_outer.exists():
        old_outer.rename(new_outer)
        new_inner = new_outer / package_name
        old_inner_after_outer = new_outer / "package_name"
        if old_inner_after_outer.exists():
            old_inner_after_outer.rename(new_inner)
    elif rendered_outer.exists() and rendered_inner.exists():
        new_outer = rendered_outer
    else:
        raise SystemExit(
            f"Expected scaffold directory not found: {old_outer}. "
            "If this package was already rendered, ensure --package-name matches the existing rendered package name."
        )

    replacements = {
        "package_name": package_name,
        "replace-me": project_name,
        "replace_me": package_name,
        "your-domain.example.com": args.domain,
        "MCP Deployment Package": f"{args.business_name} MCP Deployment Package",
        "MCP Service": service_description,
    }

    for path in root.rglob("*"):
        if path.is_file():
            replace_in_file(path, replacements)

    print(f"Rendered package at: {root}")
    print(f"Package name: {package_name}")
    print(f"Project name: {project_name}")


if __name__ == "__main__":
    main()
