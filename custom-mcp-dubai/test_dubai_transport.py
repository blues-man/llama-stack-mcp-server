#!/usr/bin/env python3

import asyncio
import sys
import os

# Add the current directory to the path so we can import our module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dubai_transport import (
    get_available_routes,
    get_route_schedule,
    find_next_bus,
    add_custom_route
)


async def test_available_routes():
    """Test the get_available_routes function."""
    print("=== Testing Available Routes ===")

    result = await get_available_routes()
    print(result)
    print("\n" + "="*80 + "\n")


async def test_route_schedule():
    """Test the get_route_schedule function."""
    print("=== Testing Route Schedule ===")

    # Test with SH1 route
    result = await get_route_schedule("SH1")
    print("Route SH1 Schedule:")
    print(result)
    print("\n" + "="*80 + "\n")


async def test_find_next_bus():
    """Test the find_next_bus function."""
    print("=== Testing Find Next Bus ===")

    # Test finding next bus for route D03 at 10:00
    result = await find_next_bus("D03", "10:00")
    print("Next bus for D03 after 10:00:")
    print(result)
    print("\n" + "="*80 + "\n")


async def test_invalid_route():
    """Test error handling with invalid route."""
    print("=== Testing Invalid Route ===")

    result = await get_route_schedule("INVALID999")
    print("Invalid Route Test:")
    print(result)
    print("\n" + "="*80 + "\n")


async def test_invalid_time():
    """Test error handling with invalid time format."""
    print("=== Testing Invalid Time Format ===")

    result = await find_next_bus("SH1", "25:99")
    print("Invalid Time Test:")
    print(result)
    print("\n" + "="*80 + "\n")


async def test_add_custom_route():
    """Test adding a custom route."""
    print("=== Testing Add Custom Route ===")

    result = await add_custom_route(
        "TEST",
        "dub:01TEST:%20:H:y08",
        "bus%20TEST"
    )
    print("Add Custom Route Result:")
    print(result)

    # Verify it was added
    routes = await get_available_routes()
    print("\nUpdated Routes List:")
    print(routes)
    print("\n" + "="*80 + "\n")


async def test_afternoon_schedule():
    """Test finding afternoon buses."""
    print("=== Testing Afternoon Bus Search ===")

    result = await find_next_bus("E411", "14:30")
    print("Next bus for E411 after 14:30:")
    print(result)
    print("\n" + "="*80 + "\n")


async def main():
    """Run all tests."""
    print("Dubai Transport MCP Server Test Suite")
    print("="*80)
    print("Note: These tests require internet connection to download PDF timetables")
    print("="*80 + "\n")

    try:
        await test_available_routes()
        await test_route_schedule()
        await test_find_next_bus()
        await test_invalid_route()
        await test_invalid_time()
        await test_add_custom_route()
        await test_afternoon_schedule()

        print("✅ All tests completed!")
        print("\nNote: Some tests may show 'No schedule times found' if PDF parsing")
        print("encounters unexpected formats. Check raw content for manual verification.")

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
