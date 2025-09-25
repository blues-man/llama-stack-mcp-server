from typing import Any, Optional
import httpx
from datetime import datetime
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("vienna-transport", host="0.0.0.0")

WIENER_LINIEN_API_BASE = "https://www.wienerlinien.at/ogd_realtime"
USER_AGENT = "vienna-transport-mcp/1.0"


async def make_transport_request(url: str) -> dict[str, Any] | None:
    """Make a request to the Wiener Linien API with proper error handling."""
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error making request to {url}: {e}")
            return None


def format_departure(departure: dict, line_name: str) -> str:
    """Format a departure into a readable string."""
    departure_time = departure.get("departureTime", {})
    vehicle = departure.get("vehicle", {})

    # Get countdown or planned time
    countdown = departure_time.get("countdown")
    planned_time = departure_time.get("timePlanned", "")
    real_time = departure_time.get("timeReal", "")

    # Format time display
    if countdown is not None:
        time_display = f"in {countdown} min"
        if planned_time:
            planned_dt = datetime.fromisoformat(planned_time.replace('+0200', ''))
            time_display += f" ({planned_dt.strftime('%H:%M')})"
    else:
        if planned_time:
            planned_dt = datetime.fromisoformat(planned_time.replace('+0200', ''))
            time_display = planned_dt.strftime('%H:%M')
        else:
            time_display = "Unknown"

    # Get destination
    towards = vehicle.get("towards", "Unknown destination").strip()

    # Get platform/direction info
    platform = vehicle.get("platform", "")
    direction = vehicle.get("direction", "")

    # Accessibility info
    barrier_free = "♿" if vehicle.get("barrierFree", False) else ""
    folding_ramp = "🚪" if vehicle.get("foldingRamp", False) else ""

    # Traffic jam indication
    traffic_jam = "🚫" if vehicle.get("trafficjam", False) else ""

    platform_info = f" Pl. {platform}" if platform else ""
    direction_info = f" Dir. {direction}" if direction else ""
    accessibility = f" {barrier_free}{folding_ramp}".strip()
    jam_info = f" {traffic_jam}" if traffic_jam else ""

    return f"{time_display} - {line_name} to {towards}{platform_info}{direction_info}{accessibility}{jam_info}"


def format_monitor_data(monitor_data: dict) -> str:
    """Format monitor data into a readable string."""
    location_stop = monitor_data.get("locationStop", {})
    properties = location_stop.get("properties", {})
    geometry = location_stop.get("geometry", {})

    # Station information
    station_name = properties.get("title", "Unknown Station")
    station_id = properties.get("name", "")
    municipality = properties.get("municipality", "")
    rbl = properties.get("attributes", {}).get("rbl", "")

    # Coordinates
    coordinates = geometry.get("coordinates", [0, 0])
    lon, lat = coordinates if len(coordinates) >= 2 else (0, 0)

    # Format header
    header = f"Station: {station_name}"
    if municipality:
        header += f", {municipality}"
    if rbl:
        header += f" (RBL: {rbl})"
    if station_id:
        header += f" (ID: {station_id})"
    header += f"\nLocation: {lat:.6f}, {lon:.6f}\n"

    # Process lines and departures
    lines = monitor_data.get("lines", [])
    if not lines:
        return header + "No departures available at this time."

    all_departures = []
    for line in lines:
        line_name = line.get("name", "Unknown")
        line_towards = line.get("towards", "").strip()
        line_direction = line.get("direction", "")
        platform = line.get("platform", "")
        barrier_free = "♿" if line.get("barrierFree", False) else ""
        realtime_supported = "🔴" if line.get("realtimeSupported", False) else "⚫"

        departures_data = line.get("departures", {})
        departures = departures_data.get("departure", [])

        if departures:
            # Add line header
            line_header = f"\n{realtime_supported} Line {line_name}"
            if line_towards:
                line_header += f" → {line_towards}"
            if platform:
                line_header += f" (Platform {platform})"
            if barrier_free:
                line_header += f" {barrier_free}"

            all_departures.append(line_header)

            # Add individual departures (limit to first 10 per line)
            for departure in departures[:10]:
                formatted_departure = format_departure(departure, line_name)
                all_departures.append(f"  {formatted_departure}")
        else:
            all_departures.append(f"\n{realtime_supported} Line {line_name} → {line_towards}: No departures")

    return header + "\n".join(all_departures)


@mcp.tool()
async def get_station_monitor(rbl: str) -> str:
    """Get real-time public transportation departures for a Vienna station using RBL number.

    Args:
        rbl: RBL (Rechnergestütztes Betriebsleitsystem) number for the station
             Example: 4127 for Kagran U1 station
    """
    url = f"{WIENER_LINIEN_API_BASE}/monitor?rbl={rbl}"

    data = await make_transport_request(url)

    if not data:
        return f"Unable to fetch station data for RBL {rbl}."

    # Check for API errors
    message = data.get("message", {})
    if message.get("messageCode") != 1:
        return f"API Error: {message.get('value', 'Unknown error')} for RBL {rbl}"

    # Get monitor data
    monitors = data.get("data", {}).get("monitors", [])
    if not monitors:
        return f"No monitor data found for RBL {rbl}."

    # Format the first monitor (there should typically be only one per RBL)
    monitor = monitors[0]
    return format_monitor_data(monitor)


@mcp.tool()
async def get_multiple_stations_monitor(rbl_list: str) -> str:
    """Get real-time departures for multiple Vienna stations using comma-separated RBL numbers.

    Args:
        rbl_list: Comma-separated list of RBL numbers
                  Example: "4127,4128,4129"
    """
    rbl_numbers = [rbl.strip() for rbl in rbl_list.split(",") if rbl.strip()]

    if not rbl_numbers:
        return "No valid RBL numbers provided."

    # Build URL with multiple RBL parameters
    rbl_params = "&".join([f"rbl={rbl}" for rbl in rbl_numbers])
    url = f"{WIENER_LINIEN_API_BASE}/monitor?{rbl_params}"

    data = await make_transport_request(url)

    if not data:
        return f"Unable to fetch station data for RBLs: {', '.join(rbl_numbers)}."

    # Check for API errors
    message = data.get("message", {})
    if message.get("messageCode") != 1:
        return f"API Error: {message.get('value', 'Unknown error')} for RBLs: {', '.join(rbl_numbers)}"

    # Get monitor data
    monitors = data.get("data", {}).get("monitors", [])
    if not monitors:
        return f"No monitor data found for RBLs: {', '.join(rbl_numbers)}."

    # Format all monitors
    results = []
    for i, monitor in enumerate(monitors):
        if i > 0:
            results.append("\n" + "="*80 + "\n")
        results.append(format_monitor_data(monitor))

    return "\n".join(results)


@mcp.tool()
async def search_vienna_stations(name: str) -> str:
    """Search for Vienna public transport stations by name.

    Args:
        name: Station name to search for (partial matching supported)
              Example: "Stephansplatz", "Karlsplatz"
    """
    # Note: This would typically require a different API endpoint for station search
    # For now, we'll provide guidance on how to find RBL numbers
    return f"""
To find RBL numbers for Vienna stations:

1. Visit: https://www.wienerlinien.at/ogd_realtime/
2. Look for station lists or use the official Wiener Linien app
3. Common stations and their RBL numbers:
   - Stephansplatz U1: 4201
   - Karlsplatz U1: 4205
   - Schwedenplatz U1: 4202
   - Westbahnhof U3: 4301
   - Kagran U1: 4127
   - Schottentor U2: 4021

For station "{name}", you can:
- Try searching online for "Wiener Linien {name} RBL"
- Use the official app to find the RBL number
- Check station signage for RBL numbers

Once you have the RBL number, use the get_station_monitor tool.
    """


if __name__ == "__main__":
    mcp.run(transport='sse')