#!/usr/bin/env python3
"""
MCP sidecar for exposing FastAPI endpoints as MCP tools.

Usage:
    python mcp_sidecar.py

This script creates an MCP server that exposes selected FastAPI endpoints
as tools that can be called by MCP clients like Cline.
"""

import asyncio
import os
import sys
from typing import Any, Dict

try:
    from fastapi_mcp import FastApiMCP

    from mcp.server import stdio
    from server.main import app
except ImportError as e:
    print(f"Error importing dependencies: {e}", file=sys.stderr)
    print("Make sure you've installed requirements.txt", file=sys.stderr)
    sys.exit(1)


def get_mcp_config() -> Dict[str, Any]:
    """Get MCP configuration from environment variables."""
    return {
        "name": "vault-rag-mcp",
        "version": "1.0.0",
        "fastapi_app": app,
        "allowlist": (
            os.getenv("MCP_ALLOWLIST", "").split(",")
            if os.getenv("MCP_ALLOWLIST")
            else None
        ),
        "denylist": (
            os.getenv("MCP_DENYLIST", "").split(",")
            if os.getenv("MCP_DENYLIST")
            else None
        ),
    }


async def main():
    """Main MCP server entry point."""
    config = get_mcp_config()

    print(f"Starting MCP sidecar: {config['name']}", file=sys.stderr)

    # Create MCP server instance
    mcp_server = FastApiMCP(
        fastapi=config["fastapi_app"],
        name=config["name"],
        include_operations=config["allowlist"],
        exclude_operations=config["denylist"],
    )

    print(
        f"MCP sidecar ready. Available tools: {len(mcp_server.tools)}", file=sys.stderr
    )
    for tool in mcp_server.tools:
        print(f"  - {tool.name}", file=sys.stderr)

    # Run the MCP server via stdio transport
    async with stdio.stdio_server() as (read_stream, write_stream):
        await mcp_server.server.run(
            read_stream, write_stream, mcp_server.server.create_initialization_options()
        )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nMCP sidecar stopped.", file=sys.stderr)
    except Exception as e:
        print(f"MCP sidecar error: {e}", file=sys.stderr)
        sys.exit(1)
