from typing import Any, Optional
import httpx
from datetime import datetime
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("swiss-transport", host="0.0.0.0")

TRANSPORT_API_BASE = "http://transport.opendata.ch/v1"
USER_AGENT = "swiss-transport-mcp/1.0"


async def make_transport_request(url: str) -> dict[str, Any] | None:
    """Make a request to the Swiss Transport API with proper error handling."""
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error making request to {url}: {e}")
            return None


def format_connection(connection: dict) -> str:
    """Format a connection into a readable string."""
    from_station = connection["from"]["station"]["name"]
    to_station = connection["to"]["station"]["name"]
    departure = connection["from"]["departure"]
    arrival = connection["to"]["arrival"]
    duration = connection["duration"]
    transfers = connection["transfers"]
    products = ", ".join(connection["products"])

    # Format delay information if available
    delay_info = ""
    if connection["from"].get("delay"):
        delay_info = f" (Delay: {connection['from']['delay']} min)"

    # Format platform information
    platform_info = ""
    if connection["from"].get("platform"):
        platform_info = f" Platform: {connection['from']['platform']}"

    return f"""
    From: {from_station} at {departure}{delay_info}{platform_info}
    To: {to_station} at {arrival}
    Duration: {duration.replace('00d', '').replace(':00', ' hours ').replace(':', ':')}
    Transfers: {transfers}
    Transport: {products}
    """


def format_location(location: dict) -> str:
    """Format a location search result into a readable string."""
    return f"{location['name']} (ID: {location['id']}) - {location.get('coordinate', {}).get('x', 'N/A')}, {location.get('coordinate', {}).get('y', 'N/A')}"


@mcp.tool()
async def search_connections(
    from_location: str,
    to_location: str,
    date: Optional[str] = None,
    time: Optional[str] = None,
    limit: int = 4
) -> str:
    """Search for public transportation connections between two locations.

    Args:
        from_location: Starting location (station name or coordinates)
        to_location: Destination location (station name or coordinates)
        date: Date in YYYY-MM-DD format (optional, defaults to today)
        time: Time in HH:MM format (optional, defaults to now)
        limit: Maximum number of connections to return (default: 4)
    """
    params = {
        "from": from_location,
        "to": to_location,
        "limit": str(limit)
    }

    if date:
        params["date"] = date
    if time:
        params["time"] = time

    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    url = f"{TRANSPORT_API_BASE}/connections?{query_string}"

    data = await make_transport_request(url)

    if not data or "connections" not in data:
        return "Unable to fetch connections or no connections found."

    if not data["connections"]:
        return f"No connections found from {from_location} to {to_location}."

    connections = [format_connection(conn) for conn in data["connections"]]

    header = f"Connections from {data['from']['name']} to {data['to']['name']}:\n"
    return header + "\n---\n".join(connections)


@mcp.tool()
async def search_locations(query: str, limit: int = 10) -> str:
    """Search for stations and locations by name.

    Args:
        query: Search query for location name
        limit: Maximum number of results to return (default: 10)
    """
    params = {
        "query": query,
        "limit": str(limit)
    }

    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    url = f"{TRANSPORT_API_BASE}/locations?{query_string}"

    data = await make_transport_request(url)

    if not data or "stations" not in data:
        return "Unable to fetch locations or no locations found."

    if not data["stations"]:
        return f"No locations found for query: {query}"

    locations = [format_location(station) for station in data["stations"]]
    return f"Locations matching '{query}':\n" + "\n".join(locations)


@mcp.tool()
async def get_stationboard(
    station: str,
    limit: int = 10,
    transportation_types: Optional[str] = None
) -> str:
    """Get departure board for a specific station.

    Args:
        station: Station name or ID
        limit: Maximum number of departures to return (default: 10)
        transportation_types: Comma-separated list of transport types (train, tram, bus, ship)
    """
    params = {
        "station": station,
        "limit": str(limit)
    }

    if transportation_types:
        params["transportations"] = transportation_types

    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    url = f"{TRANSPORT_API_BASE}/stationboard?{query_string}"

    data = await make_transport_request(url)

    if not data or "stationboard" not in data:
        return "Unable to fetch station board or no departures found."

    if not data["stationboard"]:
        return f"No departures found for station: {station}"

    departures = []
    for departure in data["stationboard"]:
        time = departure.get("stop", {}).get("departure", "N/A")
        destination = departure.get("to", "Unknown destination")
        category = departure.get("category", "")
        number = departure.get("number", "")
        platform = departure.get("stop", {}).get("platform", "")
        delay = departure.get("stop", {}).get("delay", 0)

        delay_text = f" (+{delay} min)" if delay else ""
        platform_text = f" Pl. {platform}" if platform else ""

        departures.append(f"{time}{delay_text} - {category} {number} to {destination}{platform_text}")

    station_name = data.get("station", {}).get("name", station)
    return f"Departures from {station_name}:\n" + "\n".join(departures)


if __name__ == "__main__":
    mcp.run(transport='sse')