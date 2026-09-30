"""Launch the vendored MaStR MCP server with the repo-root ``.env`` loaded.

``mastr_mcp`` only auto-loads ``mastr-mcp-server/.env``; this shim loads the
root ``.env`` first so a single credentials file serves both the MCP server
and the analysis code.

    uv run python -m mastr_analysis.mcp_server
"""

# ruff: noqa: I001  — import order is deliberate: config must load .env before mastr_mcp

from __future__ import annotations

import mastr_analysis.config  # noqa: F401
from mastr_mcp import mcp

if __name__ == "__main__":
    mcp.run(transport="stdio")
