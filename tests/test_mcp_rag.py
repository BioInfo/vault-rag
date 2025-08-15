#!/usr/bin/env python3
"""
Test script to verify MCP sidecar can call Vault RAG retrieve functionality.
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


async def test_rag_retrieve():
    """Test the RAG retrieve functionality through MCP."""
    print("=== Testing RAG Retrieve via MCP ===")

    # Test via direct HTTP call first
    async with httpx.AsyncClient() as client:
        test_query = {"query": "test query", "top_k": 3}

        try:
            print(f"Testing retrieve with query: '{test_query['query']}'")
            response = await client.post(
                "http://127.0.0.1:8000/retrieve", json=test_query, timeout=30.0
            )

            if response.status_code == 200:
                result = response.json()
                print("✓ Retrieve successful")
                print(f"  - Query: {result['query']}")
                print(f"  - Total matches: {result['total_matches']}")
                print(f"  - Sources: {len(result['sources'])} files")
                print(f"  - Matches returned: {len(result['matches'])}")

                if result["matches"]:
                    print("  - First match preview:")
                    first_match = result["matches"][0]
                    preview = (
                        first_match["text"][:100] + "..."
                        if len(first_match["text"]) > 100
                        else first_match["text"]
                    )
                    print(f"    Text: {preview}")
                    print(f"    Score: {first_match['score']:.4f}")

                return True
            else:
                print(f"✗ Retrieve failed: {response.status_code}")
                print(f"  Response: {response.text}")
                return False

        except Exception as e:
            print(f"✗ Retrieve error: {e}")
            return False


async def test_mcp_tool_schemas():
    """Test that MCP tools have proper schemas for the RAG endpoints."""
    print("\n=== Testing MCP Tool Schemas ===")

    mcp_server = FastApiMCP(fastapi=app, name="vault-rag-schema-test")

    for tool in mcp_server.tools:
        if "retrieve" in tool.name:
            print(f"✓ Found retrieve tool: {tool.name}")

            # Check if tool has proper input schema
            if hasattr(tool, "inputSchema") and tool.inputSchema:
                schema = tool.inputSchema
                print("✓ Tool has input schema")

                # Check for required fields
                if "properties" in schema:
                    props = schema["properties"]
                    if "query" in props:
                        print("✓ Query parameter defined")
                    if "top_k" in props:
                        print("✓ top_k parameter defined")

                    print(f"  Schema properties: {list(props.keys())}")

            return True

    print("✗ No retrieve tool found")
    return False


async def main():
    """Main test function."""
    print("Testing Vault RAG MCP Integration...")

    # Test RAG functionality
    rag_success = await test_rag_retrieve()

    # Test MCP schemas
    schema_success = await test_mcp_tool_schemas()

    print("\n=== RAG MCP Test Results ===")
    print(f"RAG Retrieve Functionality: {'✓' if rag_success else '✗'}")
    print(f"MCP Tool Schemas: {'✓' if schema_success else '✗'}")

    if rag_success and schema_success:
        print("🎉 Vault RAG MCP integration is fully functional!")
        print("📋 Available for agent tool calls via MCP protocol")
        return 0
    else:
        print("❌ Some RAG tests failed.")
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
