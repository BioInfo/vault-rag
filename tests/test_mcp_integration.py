#!/usr/bin/env python3
"""
Test script to verify MCP sidecar integration with Vault RAG app.
"""

import asyncio
import sys

try:
    import httpx
    from fastapi_mcp import FastApiMCP

    from server.main import app
except ImportError as e:
    print(f"Error importing dependencies: {e}", file=sys.stderr)
    sys.exit(1)


async def test_mcp_tools():
    """Test that MCP tools are generated correctly from FastAPI app."""
    print("=== Testing MCP Sidecar Integration ===")

    # Create MCP server instance
    mcp_server = FastApiMCP(
        fastapi=app,
        name="vault-rag-test",
    )

    print("✓ MCP server created successfully")
    print(f"✓ Total tools available: {len(mcp_server.tools)}")

    # List all available tools
    print("\n=== Available MCP Tools ===")
    for tool in mcp_server.tools:
        print(f"  - {tool.name}")
        if hasattr(tool, "description"):
            print(f"    Description: {tool.description}")

    # Test that we have the expected endpoints
    expected_tools = ["health", "retrieve", "root"]
    available_tool_names = [tool.name for tool in mcp_server.tools]

    print("\n=== Tool Verification ===")
    for expected in expected_tools:
        if expected in available_tool_names:
            print(f"✓ {expected} tool available")
        else:
            print(f"✗ {expected} tool missing")

    return len(mcp_server.tools) > 0


async def test_fastapi_endpoints():
    """Test that FastAPI endpoints are accessible."""
    print("\n=== Testing FastAPI Endpoints ===")

    async with httpx.AsyncClient() as client:
        # Test health endpoint
        try:
            response = await client.get("http://127.0.0.1:8000/health")
            if response.status_code == 200:
                health_data = response.json()
                print(f"✓ Health endpoint: {health_data['status']}")
                print(f"✓ Collections: {health_data['collections']}")
            else:
                print(f"✗ Health endpoint failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ Health endpoint error: {e}")
            return False

        # Test root endpoint
        try:
            response = await client.get("http://127.0.0.1:8000/")
            if response.status_code == 200:
                root_data = response.json()
                print(f"✓ Root endpoint: {root_data['message']}")
            else:
                print(f"✗ Root endpoint failed: {response.status_code}")
        except Exception as e:
            print(f"✗ Root endpoint error: {e}")

    return True


async def main():
    """Main test function."""
    print("Starting MCP integration tests...")

    # Test MCP tools generation
    mcp_success = await test_mcp_tools()

    # Test FastAPI endpoints
    api_success = await test_fastapi_endpoints()

    print("\n=== Test Results ===")
    print(f"MCP Tools Generated: {'✓' if mcp_success else '✗'}")
    print(f"FastAPI Endpoints: {'✓' if api_success else '✗'}")

    if mcp_success and api_success:
        print("🎉 All tests passed! MCP sidecar is ready for use.")
        return 0
    else:
        print("❌ Some tests failed. Check the output above.")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nTest interrupted.")
        sys.exit(1)
    except Exception as e:
        print(f"Test error: {e}")
        sys.exit(1)
