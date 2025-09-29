#!/usr/bin/env python3

import asyncio
import sys
import os

# Add the current directory to the path so we can import our module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from riyadh_transport import search_bus_routes, get_route_details, list_all_routes, search_routes_by_area


async def test_list_routes():
    """Test the list_all_routes function."""
    print("=== Testing Route Listing ===")

    result = await list_all_routes(limit=5)
    print("List of 5 bus routes:")
    print(result)
    print("\n" + "="*80 + "\n")


async def test_search_routes():
    """Test the search_bus_routes function."""
    print("=== Testing Bus Route Search ===")

    # Test search by route number
    result = await search_bus_routes(route_number="7")
    print("Search for route number '7':")
    print(result)
    print("\n" + "="*80 + "\n")

    # Test general search for university
    result = await search_bus_routes(query="University")
    print("Search for 'University':")
    print(result)
    print("\n" + "="*80 + "\n")


async def test_route_details():
    """Test the get_route_details function."""
    print("=== Testing Route Details ===")

    # Test with a known route code
    result = await get_route_details("L19-1")
    print("Details for route 'L19-1':")
    print(result)
    print("\n" + "="*80 + "\n")


async def test_area_search():
    """Test the search_routes_by_area function."""
    print("=== Testing Area Search ===")

    result = await search_routes_by_area("King", limit=5)
    print("Routes serving areas with 'King' in the name:")
    print(result)
    print("\n" + "="*80 + "\n")

    result = await search_routes_by_area("Riyadh", limit=3)
    print("Routes serving 'Riyadh' area:")
    print(result)
    print("\n" + "="*80 + "\n")


async def test_error_handling():
    """Test error handling with invalid inputs."""
    print("=== Testing Error Handling ===")

    result = await get_route_details("INVALID-ROUTE")
    print("Details for invalid route:")
    print(result)
    print("\n" + "="*80 + "\n")

    result = await search_routes_by_area("NonexistentArea")
    print("Search for non-existent area:")
    print(result)
    print("\n" + "="*80 + "\n")


async def main():
    """Run all tests."""
    print("Riyadh Transport MCP Server Test Suite")
    print("="*80)

    try:
        await test_list_routes()
        await test_search_routes()
        await test_route_details()
        await test_area_search()
        await test_error_handling()

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