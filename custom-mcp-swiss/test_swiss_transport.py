#!/usr/bin/env python3

import asyncio
import sys
import os

# Add the current directory to the path so we can import our module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from swiss_transport import search_connections, search_locations, get_stationboard


async def test_search_connections():
    """Test the search_connections function."""
    print("=== Testing Connection Search ===")

    # Test basic connection search
    result = await search_connections("Zurich", "Basel")
    print("Zurich to Basel:")
    print(result)
    print("\n" + "="*50 + "\n")

    # Test with specific time
    result = await search_connections("Geneva", "Bern", time="14:30")
    print("Geneva to Bern at 14:30:")
    print(result)
    print("\n" + "="*50 + "\n")


async def test_search_locations():
    """Test the search_locations function."""
    print("=== Testing Location Search ===")

    result = await search_locations("Zurich", limit=5)
    print("Locations matching 'Zurich':")
    print(result)
    print("\n" + "="*50 + "\n")


async def test_get_stationboard():
    """Test the get_stationboard function."""
    print("=== Testing Station Board ===")

    result = await get_stationboard("Zurich HB", limit=8)
    print("Departures from Zurich HB:")
    print(result)
    print("\n" + "="*50 + "\n")


async def main():
    """Run all tests."""
    print("Swiss Transport MCP Server Test Suite")
    print("="*50)

    try:
        await test_search_locations()
        await test_search_connections()
        await test_get_stationboard()

        print("✅ All tests completed successfully!")

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)