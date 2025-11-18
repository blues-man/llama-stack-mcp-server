from typing import Any, Optional
import httpx
import os
import re
from datetime import datetime, timedelta
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("helsinki-transport", host="0.0.0.0")

DIGITRANSIT_API_URL = "https://api.digitransit.fi/routing/v2/hsl/gtfs/v1"
DIGITRANSIT_API_KEY = os.getenv("DIGITRANSIT_API_KEY", "your_key")
DEFAULT_STOP_ID = os.getenv("DEFAULT_STOP_ID", "HSL:1040129")  # Arkadian puisto
USER_AGENT = "helsinki-transport-mcp/1.0"


async def make_graphql_request(query: str) -> dict[str, Any] | None:
    """Make a GraphQL request to the Helsinki Digitransit API with proper error handling."""
    headers = {
        "User-Agent": USER_AGENT,
        "Content-Type": "application/json",
        "digitransit-subscription-key": DIGITRANSIT_API_KEY
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                DIGITRANSIT_API_URL,
                headers=headers,
                json={"query": query},
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error making GraphQL request: {e}")
            return None


async def geocode_location(location_name: str) -> tuple[float, float, str] | None:
    """Geocode a location name to coordinates using Digitransit Geocoding API.

    Args:
        location_name: Name of the location to geocode

    Returns:
        Tuple of (latitude, longitude, label) or None if geocoding fails
    """
    url = "https://api.digitransit.fi/geocoding/v1/search"
    params = {
        "text": location_name,
        "size": 1
    }
    headers = {
        "digitransit-subscription-key": DIGITRANSIT_API_KEY
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params, headers=headers, timeout=10.0)
            response.raise_for_status()
            data = response.json()

            features = data.get("features", [])
            if features and len(features) > 0:
                coords = features[0]["geometry"]["coordinates"]
                lon, lat = coords  # GeoJSON uses [lon, lat] order
                label = features[0]["properties"].get("label", location_name)
                return (lat, lon, label)
            return None
        except Exception as e:
            print(f"Error geocoding location: {e}")
            return None


def format_time(service_day: int, seconds: int) -> str:
    """Convert service day and seconds to readable time string."""
    timestamp = service_day + seconds
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime("%H:%M:%S")


def format_departure(stoptime: dict, service_day: int) -> str:
    """Format a departure into a readable string."""
    scheduled_dep = stoptime.get("scheduledDeparture", 0)
    realtime_dep = stoptime.get("realtimeDeparture", scheduled_dep)
    delay = stoptime.get("departureDelay", 0)
    headsign = stoptime.get("headsign", "Unknown destination")

    trip = stoptime.get("trip", {})
    route_short_name = trip.get("routeShortName", "N/A")

    scheduled_time = format_time(service_day, scheduled_dep)

    # Format time with delay if applicable
    time_info = scheduled_time
    if delay > 0:
        time_info = f"{scheduled_time} (Delayed by {delay}s)"
    elif delay < 0:
        time_info = f"{scheduled_time} (Early by {abs(delay)}s)"

    return f"{time_info} - Route {route_short_name} to {headsign}"


def format_arrival(stoptime: dict, service_day: int) -> str:
    """Format an arrival into a readable string."""
    scheduled_arr = stoptime.get("scheduledArrival", 0)
    realtime_arr = stoptime.get("realtimeArrival", scheduled_arr)
    delay = stoptime.get("arrivalDelay", 0)
    headsign = stoptime.get("headsign", "Unknown origin")

    trip = stoptime.get("trip", {})
    route_short_name = trip.get("routeShortName", "N/A")

    scheduled_time = format_time(service_day, scheduled_arr)

    # Format time with delay if applicable
    time_info = scheduled_time
    if delay > 0:
        time_info = f"{scheduled_time} (Delayed by {delay}s)"
    elif delay < 0:
        time_info = f"{scheduled_time} (Early by {abs(delay)}s)"

    return f"{time_info} - Route {route_short_name} from {headsign}"


@mcp.tool()
async def get_departures(
    stop_id: str = DEFAULT_STOP_ID,
    limit: int = 10
) -> str:
    """Get real-time departures for a Helsinki public transport stop.

    Use this tool to see upcoming departures from a specific stop.
    No session ID or authentication required.

    Args:
        stop_id: The stop ID in HSL format (e.g., "HSL:1040129").
                 Use the find_stop tool first if you don't know the stop ID.
                 Default is HSL:1040129 (Arkadian puisto).
        limit: Maximum number of departures to return. Default is 10.

    Returns:
        A formatted string showing departure times, routes, and destinations.
        Includes delay information if available.
    """
    query = f"""
    {{
      stop(id: "{stop_id}") {{
        name
        gtfsId
        stoptimesWithoutPatterns(numberOfDepartures: {limit}) {{
          scheduledDeparture
          realtimeDeparture
          departureDelay
          realtime
          serviceDay
          headsign
          trip {{
            routeShortName
            route {{
              shortName
              longName
            }}
          }}
        }}
      }}
    }}
    """

    data = await make_graphql_request(query)

    if not data or "data" not in data or not data["data"].get("stop"):
        return f"Unable to fetch departures for stop ID: {stop_id}"

    stop_data = data["data"]["stop"]
    stop_name = stop_data.get("name", "Unknown stop")
    stoptimes = stop_data.get("stoptimesWithoutPatterns", [])

    if not stoptimes:
        return f"No departures found for stop: {stop_name} ({stop_id})"

    # Get service day from first stoptime
    service_day = stoptimes[0].get("serviceDay", 0)

    departures = [format_departure(st, service_day) for st in stoptimes]

    return f"Departures from {stop_name} ({stop_id}):\n" + "\n".join(departures)


@mcp.tool()
async def get_timetable(
    stop_id: str = DEFAULT_STOP_ID,
    start_time: int = 0,
    time_range: int = 3600
) -> str:
    """Get timetable for a Helsinki public transport stop within a time range.

    Use this tool to see scheduled departures for a specific time window.
    No session ID or authentication required.

    Args:
        stop_id: The stop ID in HSL format (e.g., "HSL:1040129").
                 Use the find_stop tool first if you don't know the stop ID.
                 Default is HSL:1040129 (Arkadian puisto).
        start_time: Start time in seconds from midnight. Use 0 for current time. Default is 0.
        time_range: Time range in seconds from start_time. Default is 3600 (1 hour).

    Returns:
        A formatted string showing scheduled departures within the time range.
    """
    query = f"""
    {{
      stop(id: "{stop_id}") {{
        name
        gtfsId
        stoptimesWithoutPatterns(
          startTime: {start_time}
          timeRange: {time_range}
          numberOfDepartures: 50
        ) {{
          scheduledDeparture
          realtimeDeparture
          departureDelay
          realtime
          serviceDay
          headsign
          trip {{
            routeShortName
            route {{
              shortName
              longName
            }}
          }}
        }}
      }}
    }}
    """

    data = await make_graphql_request(query)

    if not data or "data" not in data or not data["data"].get("stop"):
        return f"Unable to fetch timetable for stop ID: {stop_id}"

    stop_data = data["data"]["stop"]
    stop_name = stop_data.get("name", "Unknown stop")
    stoptimes = stop_data.get("stoptimesWithoutPatterns", [])

    if not stoptimes:
        return f"No timetable entries found for stop: {stop_name} ({stop_id})"

    # Get service day from first stoptime
    service_day = stoptimes[0].get("serviceDay", 0)

    departures = [format_departure(st, service_day) for st in stoptimes]

    time_range_minutes = time_range // 60
    return f"Timetable for {stop_name} ({stop_id}) - Next {time_range_minutes} minutes:\n" + "\n".join(departures)


@mcp.tool()
async def get_stop_info(stop_id: str) -> str:
    """Get detailed information about a specific Helsinki public transport stop.

    Use this tool to get stop details like name, location, zone, and platform.
    No session ID or authentication required.

    Args:
        stop_id: The stop ID in HSL format (e.g., "HSL:1040129").
                 Use the find_stop tool first if you don't know the stop ID.

    Returns:
        A formatted string with stop name, ID, code, description, coordinates,
        zone, and platform information.
    """
    query = f"""
    {{
      stop(id: "{stop_id}") {{
        name
        gtfsId
        code
        desc
        lat
        lon
        zoneId
        locationType
        platformCode
      }}
    }}
    """

    data = await make_graphql_request(query)

    if not data or "data" not in data or not data["data"].get("stop"):
        return f"Unable to fetch information for stop ID: {stop_id}"

    stop = data["data"]["stop"]

    result = f"""Stop Information:
Name: {stop.get('name', 'N/A')}
GTFS ID: {stop.get('gtfsId', 'N/A')}
Code: {stop.get('code', 'N/A')}
Description: {stop.get('desc', 'N/A')}
Location: {stop.get('lat', 'N/A')}, {stop.get('lon', 'N/A')}
Zone: {stop.get('zoneId', 'N/A')}
Platform: {stop.get('platformCode', 'N/A')}
"""

    return result


@mcp.tool()
async def find_stop(query: str, limit: int = 10, radius: int = 500) -> str:
    """Find public transport stops by name or location in Helsinki area.

    Use this tool to search for stops and get their stop IDs needed for other tools.
    No session ID or authentication required - just provide a search query.

    Supports two search modes:
    1. Name search: Just provide the stop name (e.g., "Kamppi", "Rautatientori")
    2. Location search: Use natural language (e.g., "near Scandic Grand Marina", "close to Senate Square")

    Args:
        query: The search query. Can be either:
               - A stop name: "Kamppi", "Rautatientori", "central station"
               - A location phrase: "near [place]", "close to [place]", "around [place]"
        limit: Maximum number of results to return. Default is 10.
        radius: Search radius in meters for location-based searches. Default is 500.

    Returns:
        A formatted string with stop IDs, names, codes, locations, and coordinates.
        For location searches, also includes distance in meters.
    """
    # Detect if this is a location-based query
    location_patterns = [
        r"(?:near|close to|around|by|at|in)\s+(.+)",
        r"(.+?)\s+(?:area|vicinity|neighborhood)",
        r"stops?\s+(?:near|around|at|in)\s+(.+)"
    ]

    location_name = None
    for pattern in location_patterns:
        match = re.search(pattern, query, re.IGNORECASE)
        if match:
            location_name = match.group(1).strip()
            break

    # If location-based query, use geocoding + nearest
    if location_name:
        geocode_result = await geocode_location(location_name)
        if not geocode_result:
            return f"Unable to find location: {location_name}"

        lat, lon, label = geocode_result

        # Use the nearest query to find stops
        graphql_query = f"""
        {{
          nearest(
            lat: {lat},
            lon: {lon},
            maxDistance: {radius},
            first: {limit},
            filterByPlaceTypes: STOP
          ) {{
            edges {{
              node {{
                place {{
                  ...on Stop {{
                    gtfsId
                    name
                    code
                    desc
                    lat
                    lon
                  }}
                }}
                distance
              }}
            }}
          }}
        }}
        """

        data = await make_graphql_request(graphql_query)

        if not data or "data" not in data or not data["data"].get("nearest"):
            return f"Unable to find stops near: {label}"

        edges = data["data"]["nearest"].get("edges", [])

        if not edges:
            return f"No stops found within {radius}m of: {label}"

        results = []
        for edge in edges:
            node = edge["node"]
            stop = node["place"]
            distance = node["distance"]

            stop_id = stop.get("gtfsId", "N/A")
            stop_name = stop.get("name", "N/A")
            code = stop.get("code", "N/A")
            desc = stop.get("desc", "N/A")
            stop_lat = stop.get("lat", "N/A")
            stop_lon = stop.get("lon", "N/A")

            results.append(
                f"ID: {stop_id} ({distance}m away)\n"
                f"  Name: {stop_name}\n"
                f"  Code: {code}\n"
                f"  Location: {desc}\n"
                f"  Coordinates: {stop_lat}, {stop_lon}"
            )

        header = f"Found {len(edges)} stop(s) near {label}:\n\n"
        return header + "\n\n".join(results)

    # Otherwise, use name-based search
    else:
        graphql_query = f"""
        {{
          stops(name: "{query}") {{
            gtfsId
            name
            code
            desc
            lat
            lon
          }}
        }}
        """

        data = await make_graphql_request(graphql_query)

        if not data or "data" not in data:
            return f"Unable to search for stops with name: {query}"

        stops = data["data"].get("stops", [])

        if not stops:
            return f"No stops found matching: {query}"

        # Limit results
        stops = stops[:limit]

        results = []
        for stop in stops:
            stop_id = stop.get("gtfsId", "N/A")
            stop_name = stop.get("name", "N/A")
            code = stop.get("code", "N/A")
            desc = stop.get("desc", "N/A")
            lat = stop.get("lat", "N/A")
            lon = stop.get("lon", "N/A")

            results.append(
                f"ID: {stop_id}\n"
                f"  Name: {stop_name}\n"
                f"  Code: {code}\n"
                f"  Location: {desc}\n"
                f"  Coordinates: {lat}, {lon}"
            )

        header = f"Found {len(stops)} stop(s) matching '{query}':\n\n"
        return header + "\n\n".join(results)


if __name__ == "__main__":
    mcp.run(transport='sse')
