from typing import Any, Optional
import httpx
import os
from datetime import datetime
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("stockholm-transport", host="0.0.0.0")

TRANSPORT_API_BASE = "https://realtime-api.trafiklab.se/v1"
TRANSPORT_API_KEY = os.getenv("API_KEY", "3d2a9300eef04982a43bf819b07113ab")
STOCKHOLM_AREA_ID = os.getenv("STOCKHOLM_AREA_ID", "740098000")
USER_AGENT = "stockholm-transport-mcp/1.0"


async def make_transport_request(url: str) -> dict[str, Any] | None:
    """Make a request to the Stockholm Transport API with proper error handling."""
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error making request to {url}: {e}")
            return None


def format_departure(departure: dict) -> str:
    """Format a departure into a readable string."""
    stop_name = departure.get("stop_area_name", "Unknown stop")
    line_number = departure.get("line_number", "")
    line_designation = departure.get("line_designation", "")
    destination = departure.get("destination", "Unknown destination")
    display_time = departure.get("display_time", "N/A")
    expected_time = departure.get("expected", "")
    journey_direction = departure.get("journey_direction", "")

    # Format time with delay if applicable
    time_info = display_time
    if expected_time and expected_time != display_time:
        time_info = f"{display_time} (Expected: {expected_time})"

    return f"{time_info} - Line {line_number} {line_designation} to {destination}"


def format_arrival(arrival: dict) -> str:
    """Format an arrival into a readable string."""
    stop_name = arrival.get("stop_area_name", "Unknown stop")
    line_number = arrival.get("line_number", "")
    line_designation = arrival.get("line_designation", "")
    origin = arrival.get("origin", "Unknown origin")
    display_time = arrival.get("display_time", "N/A")
    expected_time = arrival.get("expected", "")

    # Format time with delay if applicable
    time_info = display_time
    if expected_time and expected_time != display_time:
        time_info = f"{display_time} (Expected: {expected_time})"

    return f"{time_info} - Line {line_number} {line_designation} from {origin}"


@mcp.tool()
async def get_departures(
    area_id: str = STOCKHOLM_AREA_ID,
    limit: int = 10
) -> str:
    """Get departures for Stockholm public transportation.

    Args:
        area_id: Area ID for the location (default: Stockholm area 740098000)
        limit: Maximum number of departures to return (default: 10)
    """
    url = f"{TRANSPORT_API_BASE}/departures/{area_id}?key={TRANSPORT_API_KEY}"

    data = await make_transport_request(url)

    if not data or "departures" not in data:
        return "Unable to fetch departures or no departures found."

    if not data["departures"]:
        return f"No departures found for area ID: {area_id}"

    departures = [format_departure(dep) for dep in data["departures"][:limit]]

    return f"Departures for area {area_id}:\n" + "\n".join(departures)


@mcp.tool()
async def get_arrivals(
    area_id: str = STOCKHOLM_AREA_ID,
    limit: int = 10
) -> str:
    """Get arrivals for Stockholm public transportation.

    Args:
        area_id: Area ID for the location (default: Stockholm area 740098000)
        limit: Maximum number of arrivals to return (default: 10)
    """
    url = f"{TRANSPORT_API_BASE}/arrivals/{area_id}?key={TRANSPORT_API_KEY}"

    data = await make_transport_request(url)

    if not data or "arrivals" not in data:
        return "Unable to fetch arrivals or no arrivals found."

    if not data["arrivals"]:
        return f"No arrivals found for area ID: {area_id}"

    arrivals = [format_arrival(arr) for arr in data["arrivals"][:limit]]

    return f"Arrivals for area {area_id}:\n" + "\n".join(arrivals)


@mcp.tool()
async def get_departures_and_arrivals(
    area_id: str = STOCKHOLM_AREA_ID,
    limit: int = 10
) -> str:
    """Get both departures and arrivals for Stockholm public transportation.

    Args:
        area_id: Area ID for the location (default: Stockholm area 740098000)
        limit: Maximum number of departures/arrivals to return (default: 10)
    """
    departures_result = await get_departures(area_id, limit)
    arrivals_result = await get_arrivals(area_id, limit)

    return f"{departures_result}\n\n{arrivals_result}"


if __name__ == "__main__":
    mcp.run(transport='sse')