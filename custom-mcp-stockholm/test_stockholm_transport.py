#!/usr/bin/env python3

import asyncio
import sys
import os

# Add the current directory to the path so we can import our module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from stockholm_transport import get_departures, get_arrivals, get_departures_and_arrivals


async def test_get_departures():
    """Test the get_departures function."""
    print("=== Testing Departures ===")

    # Test departures for Stockholm area
    result = await get_departures(limit=5)
    print("Departures for Stockholm area:")
    print(result)
    print("\n" + "="*50 + "\n")


async def test_get_arrivals():
    """Test the get_arrivals function."""
    print("=== Testing Arrivals ===")

    # Test arrivals for Stockholm area
    result = await get_arrivals(limit=5)
    print("Arrivals for Stockholm area:")
    print(result)
    print("\n" + "="*50 + "\n")


async def test_get_departures_and_arrivals():
    """Test the get_departures_and_arrivals function."""
    print("=== Testing Departures and Arrivals ===")

    result = await get_departures_and_arrivals(limit=5)
    print("Departures and Arrivals for Stockholm area:")
    print(result)
    print("\n" + "="*50 + "\n")


async def main():
    """Run all tests."""
    print("Stockholm Transport MCP Server Test Suite")
    print("="*50)

    try:
        await test_get_departures()
        await test_get_arrivals()
        await test_get_departures_and_arrivals()

        print("✅ All tests completed successfully!")

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)