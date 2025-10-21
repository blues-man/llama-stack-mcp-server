#!/usr/bin/env python3

import asyncio
import sys
import os

# Add the current directory to the path so we can import our module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from helsinki_transport import get_departures, get_timetable, get_stop_info


async def test_get_departures():
    """Test the get_departures function."""
    print("=== Testing Departures ===")

    # Test departures for default stop (Arkadian puisto)
    result = await get_departures(limit=5)
    print("Departures for default Helsinki stop (Arkadian puisto):")
    print(result)
    print("\n" + "="*50 + "\n")


async def test_get_timetable():
    """Test the get_timetable function."""
    print("=== Testing Timetable ===")

    # Test timetable for default stop
    result = await get_timetable(time_range=3600, start_time=0)
    print("Timetable for default Helsinki stop (next hour):")
    print(result)
    print("\n" + "="*50 + "\n")


async def test_get_stop_info():
    """Test the get_stop_info function."""
    print("=== Testing Stop Information ===")

    # Test stop info for default stop
    result = await get_stop_info("HSL:1040129")
    print("Stop information for Arkadian puisto:")
    print(result)
    print("\n" + "="*50 + "\n")


async def test_custom_stop():
    """Test with a different stop."""
    print("=== Testing Custom Stop ===")

    # Test with Helsinki Central Railway Station
    custom_stop = "HSL:1020552"
    result = await get_departures(stop_id=custom_stop, limit=5)
    print(f"Departures for stop {custom_stop}:")
    print(result)
    print("\n" + "="*50 + "\n")


async def main():
    """Run all tests."""
    print("Helsinki Transport MCP Server Test Suite")
    print("="*50)

    try:
        await test_get_departures()
        await test_get_timetable()
        await test_get_stop_info()
        await test_custom_stop()

        print("✅ All tests completed successfully!")

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
