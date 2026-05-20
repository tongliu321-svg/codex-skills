#!/usr/bin/env python3
"""Generate a standard scaffold for a reusable MCP deployment package."""

from __future__ import annotations

import argparse
from pathlib import Path


PACKAGE_FILES = {
    ".env.example": """# Common deployment settings\nMCP_HOST=0.0.0.0\nMCP_PORT=8000\nMCP_TRANSPORT=sse\n""",
    "README_DEPLOY.md": "# MCP Deployment Package\n\nFill in business-specific deployment notes.\n",
    "start.sh": "#!/usr/bin/env bash\nset -euo pipefail\ncd \"$(dirname \"$0\")\"\nif [ -f \".env\" ]; then\n  set -a\n  source \".env\"\n  set +a\nfi\nsource .venv/bin/activate\npython ./package_name/run_mcp_server.py\n",
    "business/README.md": "# Business Files\n\nPlace business rules, mappings, and source files here.\n",
    "package_name/pyproject.toml": "[project]\nname = \"replace-me\"\nversion = \"0.1.0\"\nrequires-python = \">=3.11\"\ndependencies = [\"mcp>=1.27.0\", \"pydantic>=2.0.0\"]\n\n[build-system]\nrequires = [\"setuptools>=68\", \"wheel\"]\nbuild-backend = \"setuptools.build_meta\"\n",
    "package_name/run_mcp_server.py": "from package_name.server import main\n\nif __name__ == \"__main__\":\n    main()\n",
    "package_name/package_name/__init__.py": "",
    "package_name/package_name/models.py": "from pydantic import BaseModel\n\nclass ToolResponse(BaseModel):\n    message: str\n",
    "package_name/package_name/service.py": "from .models import ToolResponse\n\ndef run_business_logic() -> ToolResponse:\n    return ToolResponse(message=\"replace with business logic\")\n",
    "package_name/package_name/config.py": "import os\n\nHOST = os.getenv(\"MCP_HOST\", \"127.0.0.1\")\nPORT = int(os.getenv(\"MCP_PORT\", \"8000\"))\nTRANSPORT = os.getenv(\"MCP_TRANSPORT\", \"sse\")\n",
    "package_name/package_name/data_access.py": "# Add database, file, or API access here.\n",
    "package_name/package_name/rules.py": "# Add business rules here.\n",
    "package_name/package_name/server.py": "from mcp.server.fastmcp import FastMCP\nfrom .config import HOST, PORT, TRANSPORT\nfrom .service import run_business_logic\n\nmcp = FastMCP(name=\"replace_me\", host=HOST, port=PORT, sse_path=\"/sse\", streamable_http_path=\"/mcp\")\n\n@mcp.tool()\ndef business_tool() -> str:\n    return run_business_logic().model_dump_json(ensure_ascii=False)\n\ndef main() -> None:\n    mcp.run(transport=TRANSPORT)\n",
    "deploy/nginx/mcp.conf": "server {\n    listen 80;\n    server_name your-domain.example.com;\n\n    location /sse {\n        proxy_pass http://127.0.0.1:8000/sse;\n        proxy_buffering off;\n        proxy_read_timeout 3600;\n    }\n\n    location /messages/ {\n        proxy_pass http://127.0.0.1:8000/messages/;\n        proxy_read_timeout 3600;\n    }\n\n    location /mcp {\n        proxy_pass http://127.0.0.1:8000/mcp;\n        proxy_read_timeout 3600;\n    }\n}\n",
    "deploy/systemd/mcp.service": "[Unit]\nDescription=MCP Service\nAfter=network.target\n\n[Service]\nType=simple\nWorkingDirectory=/opt/package_name\nExecStart=/opt/package_name/.venv/bin/python /opt/package_name/package_name/run_mcp_server.py\nRestart=always\nRestartSec=3\n\n[Install]\nWantedBy=multi-user.target\n",
}


def write_files(root: Path, file_map: dict[str, str]) -> None:
    for relative_path, content in file_map.items():
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize a standard MCP deployment package.")
    parser.add_argument("--output", required=True, help="Output directory path.")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Allow writing into a non-empty directory.",
    )
    args = parser.parse_args()

    root = Path(args.output).expanduser().resolve()
    if root.exists():
        if any(root.iterdir()) and not args.force:
            raise SystemExit(
                f"Target directory is not empty: {root}. "
                "Use a new directory or pass --force only if you intentionally want to reuse it."
            )
    root.mkdir(parents=True, exist_ok=True)
    write_files(root, PACKAGE_FILES)

    print(f"Created scaffold at: {root}")


if __name__ == "__main__":
    main()
