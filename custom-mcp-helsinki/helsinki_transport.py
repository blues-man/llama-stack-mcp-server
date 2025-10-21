from typing import Any, Optional
import httpx
import os
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
    """Get departures for Helsinki public transportation.

    Args:
        stop_id: Stop ID in format HSL:xxxxxxx (default: HSL:1040129 - Arkadian puisto)
        limit: Maximum number of departures to return (default: 10)
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
    """Get timetable for a stop within a specific time range.

    Args:
        stop_id: Stop ID in format HSL:xxxxxxx (default: HSL:1040129 - Arkadian puisto)
        start_time: Start time in seconds from midnight (default: 0 = now)
        time_range: Time range in seconds from start_time (default: 3600 = 1 hour)
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
    """Get information about a specific stop.

    Args:
        stop_id: Stop ID in format HSL:xxxxxxx
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


if __name__ == "__main__":
    mcp.run(transport='sse')
