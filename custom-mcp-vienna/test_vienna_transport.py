#!/usr/bin/env python3

import asyncio
import sys
import os

# Add the current directory to the path so we can import our module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from vienna_transport import get_station_monitor, get_multiple_stations_monitor, search_vienna_stations


async def test_single_station():
    """Test the get_station_monitor function."""
    print("=== Testing Single Station Monitor ===")

    # Test Kagran U1 station (RBL 4127)
    result = await get_station_monitor("4127")
    print("Kagran U1 Station (RBL 4127):")
    print(result)
    print("\n" + "="*80 + "\n")


async def test_multiple_stations():
    """Test the get_multiple_stations_monitor function."""
    print("=== Testing Multiple Stations Monitor ===")

    # Test multiple popular stations
    result = await get_multiple_stations_monitor("4127,4201,4205")
    print("Multiple Stations (Kagran, Stephansplatz, Karlsplatz):")
    print(result)
    print("\n" + "="*80 + "\n")


async def test_station_search():
    """Test the search_vienna_stations function."""
    print("=== Testing Station Search ===")

    result = await search_vienna_stations("Stephansplatz")
    print("Search for 'Stephansplatz':")
    print(result)
    print("\n" + "="*80 + "\n")


async def test_invalid_rbl():
    """Test error handling with invalid RBL."""
    print("=== Testing Invalid RBL ===")

    result = await get_station_monitor("99999")
    print("Invalid RBL (99999):")
    print(result)
    print("\n" + "="*80 + "\n")


async def main():
    """Run all tests."""
    print("Vienna Transport MCP Server Test Suite")
    print("="*80)

    try:
        await test_single_station()
        await test_multiple_stations()
        await test_station_search()
        await test_invalid_rbl()

        print("✅ All tests completed successfully!")

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)