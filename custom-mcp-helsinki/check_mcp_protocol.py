#!/usr/bin/env python3
"""Check the actual MCP protocol JSON that gets sent to clients."""

import asyncio
import json
from helsinki_transport import mcp

async def check_protocol():
    """Check what the MCP server actually sends."""
    print("=" * 80)
    print("ACTUAL MCP PROTOCOL TOOL DEFINITIONS")
    print("=" * 80)
    print()

    tools = await mcp.list_tools()

    for tool in tools:
        tool_dict = {
            "name": tool.name,
            "description": tool.description,
            "inputSchema": tool.inputSchema if hasattr(tool, 'inputSchema') else None
        }

        print(f"Tool: {tool.name}")
        print(json.dumps(tool_dict, indent=2))
        print()
        print("=" * 80)
        print()

if __name__ == "__main__":
    asyncio.run(check_protocol())
