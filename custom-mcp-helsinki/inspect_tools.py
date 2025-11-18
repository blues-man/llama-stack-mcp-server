#!/usr/bin/env python3
"""Inspect MCP tool schemas to verify they're clear for LLMs."""

import asyncio
import json
from helsinki_transport import mcp

async def inspect_tools():
    """Print the tool schemas in a readable format."""
    print("=" * 80)
    print("MCP TOOL SCHEMAS")
    print("=" * 80)
    print()

    # Get the tools from the MCP server
    tools = await mcp.list_tools()

    for i, tool in enumerate(tools, 1):
        print(f"{i}. Tool: {tool.name}")
        print("-" * 80)
        print(f"Description: {tool.description}")
        print()

        if hasattr(tool, 'inputSchema') and tool.inputSchema:
            schema = tool.inputSchema
            print("Parameters:")

            if 'properties' in schema:
                for param_name, param_info in schema['properties'].items():
                    required = param_name in schema.get('required', [])
                    param_type = param_info.get('type', 'unknown')
                    param_desc = param_info.get('description', 'No description')
                    default = param_info.get('default', None)

                    print(f"  - {param_name} ({param_type}){' [REQUIRED]' if required else ''}")
                    print(f"    Description: {param_desc}")
                    if default is not None:
                        print(f"    Default: {default}")
                    print()

        print("=" * 80)
        print()

if __name__ == "__main__":
    asyncio.run(inspect_tools())
