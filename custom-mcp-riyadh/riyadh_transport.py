from typing import Any, Optional, List
import httpx
from datetime import datetime
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("riyadh-transport", host="0.0.0.0")

RIYADH_API_BASE = "https://opendata.rcrc.gov.sa/api/explore/v2.1/catalog/datasets"
DATASET_NAME = "bus-roads-by-direction-in-riyadh-2024"
USER_AGENT = "riyadh-transport-mcp/1.0"


async def make_transport_request(url: str) -> dict[str, Any] | None:
    """Make a request to the Riyadh Transport API with proper error handling."""
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error making request to {url}: {e}")
            return None


def format_bus_route(record: dict) -> str:
    """Format a bus route record into a readable string."""
    # Basic route information
    route_code = record.get("busroutecode", "Unknown")
    route_number = record.get("busroute", "N/A")
    direction = record.get("direction", "N/A")

    # Origin and destination (English and Arabic)
    origin_en = record.get("origin", "Unknown Origin")
    destination_en = record.get("destination", "Unknown Destination")
    origin_ar = record.get("originar", "")
    destination_ar = record.get("destinationar", "")

    # Geographic information - calculate center from geoshape if available
    geoshape = record.get("geoshape", {})
    lat, lon = "N/A", "N/A"
    waypoint_count = 0

    if geoshape and geoshape.get("geometry", {}).get("coordinates"):
        coords = geoshape["geometry"]["coordinates"]
        if coords:
            waypoint_count = len(coords)
            # Calculate approximate center from first and last coordinates
            first_coord = coords[0]
            last_coord = coords[-1]
            lat = (first_coord[1] + last_coord[1]) / 2
            lon = (first_coord[0] + last_coord[0]) / 2

    # Comments
    comments_en = record.get("comments", "")
    comments_ar = record.get("commentsar", "")

    # Format the output
    route_info = f"🚌 Route {route_number} ({route_code}) - Direction {direction}\n"

    # Add origin with Arabic if available
    route_info += f"📍 From: {origin_en}"
    if origin_ar and origin_ar != "NA":
        route_info += f" ({origin_ar})"
    route_info += "\n"

    # Add destination with Arabic if available
    route_info += f"🎯 To: {destination_en}"
    if destination_ar and destination_ar != "NA":
        route_info += f" ({destination_ar})"
    route_info += "\n"

    # Add geographic information
    route_info += f"🌍 Center Point: {lat}, {lon}\n"

    if waypoint_count > 0:
        route_info += f"🗺️ Route has {waypoint_count} GPS waypoints\n"

    # Add comments if available
    if comments_en and comments_en != "":
        route_info += f"💬 Notes: {comments_en}\n"
    if comments_ar and comments_ar != "":
        route_info += f"💬 Notes (AR): {comments_ar}\n"

    return route_info.rstrip()


def format_route_summary(routes: List[dict]) -> str:
    """Format a summary of multiple routes."""
    if not routes:
        return "No routes found."

    summary_lines = []
    for route in routes:
        route_code = route.get("busroutecode", "Unknown")
        route_number = route.get("busroute", "N/A")
        origin = route.get("origin", "Unknown")
        destination = route.get("destination", "Unknown")
        direction = route.get("direction", "N/A")

        summary_lines.append(f"🚌 {route_number} ({route_code}) Dir.{direction}: {origin} → {destination}")

    return "\n".join(summary_lines)


@mcp.tool()
async def search_bus_routes(
    query: Optional[str] = None,
    route_number: Optional[str] = None,
    origin: Optional[str] = None,
    destination: Optional[str] = None,
    limit: int = 10
) -> str:
    """Search for bus routes in Riyadh by various criteria.

    Args:
        query: General search query for route information
        route_number: Specific bus route number to search for
        origin: Search by origin location
        destination: Search by destination location
        limit: Maximum number of results to return (default: 10)
    """
    # Build query parameters
    params = {"limit": str(limit)}

    # Build search criteria
    where_clauses = []

    if route_number:
        where_clauses.append(f"busroute = '{route_number}'")

    if origin:
        where_clauses.append(f"origin LIKE '%{origin}%'")

    if destination:
        where_clauses.append(f"destination LIKE '%{destination}%'")

    if query:
        # General search across multiple fields
        general_search = f"(origin LIKE '%{query}%' OR destination LIKE '%{query}%' OR busroutecode LIKE '%{query}%')"
        where_clauses.append(general_search)

    if where_clauses:
        params["where"] = " AND ".join(where_clauses)

    # Make API request
    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    url = f"{RIYADH_API_BASE}/{DATASET_NAME}/records?{query_string}"

    data = await make_transport_request(url)

    if not data:
        return "Unable to fetch bus route data from Riyadh transport API."

    results = data.get("results", [])
    total_count = data.get("total_count", 0)

    if not results:
        search_criteria = []
        if route_number:
            search_criteria.append(f"route number '{route_number}'")
        if origin:
            search_criteria.append(f"origin '{origin}'")
        if destination:
            search_criteria.append(f"destination '{destination}'")
        if query:
            search_criteria.append(f"query '{query}'")

        criteria_text = ", ".join(search_criteria) if search_criteria else "specified criteria"
        return f"No bus routes found for {criteria_text}."

    # Format results
    header = f"Riyadh Bus Routes (showing {len(results)} of {total_count} total routes):\n\n"

    if len(results) == 1:
        # Show detailed information for single result
        return header + format_bus_route(results[0])
    else:
        # Show summary for multiple results
        return header + format_route_summary(results)


@mcp.tool()
async def get_route_details(route_code: str) -> str:
    """Get detailed information about a specific bus route by its route code.

    Args:
        route_code: The bus route code (e.g., "L19-1")
    """
    params = {
        "where": f"busroutecode = '{route_code}'",
        "limit": "1"
    }

    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    url = f"{RIYADH_API_BASE}/{DATASET_NAME}/records?{query_string}"

    data = await make_transport_request(url)

    if not data:
        return f"Unable to fetch details for route {route_code}."

    results = data.get("results", [])

    if not results:
        return f"Route {route_code} not found."

    route = results[0]

    # Get detailed route information including geographic data
    route_info = format_bus_route(route)

    # Add geographic route information if available
    geoshape = route.get("geoshape", {})
    if geoshape and geoshape.get("geometry", {}).get("coordinates"):
        coordinates = geoshape["geometry"]["coordinates"]
        if coordinates and len(coordinates) >= 2:
            start_coord = coordinates[0]
            end_coord = coordinates[-1]
            route_info += f"\n📍 Start GPS: {start_coord[1]:.6f}, {start_coord[0]:.6f}"
            route_info += f"\n🏁 End GPS: {end_coord[1]:.6f}, {end_coord[0]:.6f}"

    return route_info


@mcp.tool()
async def list_all_routes(limit: int = 20) -> str:
    """List all available bus routes in Riyadh.

    Args:
        limit: Maximum number of routes to return (default: 20)
    """
    params = {"limit": str(limit)}

    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    url = f"{RIYADH_API_BASE}/{DATASET_NAME}/records?{query_string}"

    data = await make_transport_request(url)

    if not data:
        return "Unable to fetch bus routes from Riyadh transport API."

    results = data.get("results", [])
    total_count = data.get("total_count", 0)

    if not results:
        return "No bus routes found in the system."

    header = f"Riyadh Public Bus Routes (showing {len(results)} of {total_count} total routes):\n\n"

    return header + format_route_summary(results)


@mcp.tool()
async def search_routes_by_area(area_name: str, limit: int = 10) -> str:
    """Search for bus routes that serve a specific area or neighborhood in Riyadh.

    Args:
        area_name: Name of the area or neighborhood to search for
        limit: Maximum number of routes to return (default: 10)
    """
    # Search in both origin and destination fields for the area name
    params = {
        "where": f"(origin LIKE '%{area_name}%' OR destination LIKE '%{area_name}%')",
        "limit": str(limit)
    }

    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    url = f"{RIYADH_API_BASE}/{DATASET_NAME}/records?{query_string}"

    data = await make_transport_request(url)

    if not data:
        return f"Unable to search for routes serving {area_name}."

    results = data.get("results", [])
    total_count = data.get("total_count", 0)

    if not results:
        return f"No bus routes found serving the area '{area_name}'."

    header = f"Bus routes serving '{area_name}' (found {len(results)} routes):\n\n"

    return header + format_route_summary(results)


if __name__ == "__main__":
    mcp.run(transport='sse')