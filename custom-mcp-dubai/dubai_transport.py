from typing import Any, Optional
import httpx
from datetime import datetime, time
from mcp.server.fastmcp import FastMCP
import io
import re
import os
import hashlib
from pathlib import Path
try:
    import pdfplumber
except ImportError:
    pdfplumber = None

mcp = FastMCP("dubai-transport", host="0.0.0.0")

RTA_API_BASE = "https://www.rta.ae/wps/PA_JourneyPlanner/DownloadTimetableServlet"
USER_AGENT = "dubai-transport-mcp/1.0"

# Cache directory for downloaded PDFs
CACHE_DIR = Path.home() / ".cache" / "dubai-transport-mcp"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Common bus routes in Dubai with their line IDs
KNOWN_ROUTES = {
    "SH1": {"lineId": "dub:01SH1:%20:H:y08", "lineName": "bus%20SH1"},
    "D03": {"lineId": "dub:01D03:%20:H:y08", "lineName": "bus%20D03"},
    "E411": {"lineId": "dub:10411:%20:H:y08", "lineName": "bus%20E411"},
    "F62": {"lineId": "dub:12F62:%20:H:y08", "lineName": "bus%20F62"},
    "8": {"lineId": "dub:00008:%20:H:y08", "lineName": "bus%208"},
    "11": {"lineId": "dub:00011:%20:H:y08", "lineName": "bus%2011"},
    "C01": {"lineId": "dub:01C01:%20:H:y08", "lineName": "bus%20C01"},
    "C10": {"lineId": "dub:01C10:%20:H:y08", "lineName": "bus%20C10"},
}


def get_cache_path(route_code: str) -> Path:
    """Get the cache file path for a route."""
    # Use route code for cache filename
    cache_filename = f"{route_code.upper()}.pdf"
    return CACHE_DIR / cache_filename


def get_cached_pdf(route_code: str) -> bytes | None:
    """Get cached PDF if it exists."""
    cache_path = get_cache_path(route_code)
    if cache_path.exists():
        try:
            with open(cache_path, 'rb') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading cached PDF: {e}")
    return None


def save_pdf_to_cache(route_code: str, pdf_content: bytes) -> None:
    """Save PDF to cache."""
    cache_path = get_cache_path(route_code)
    try:
        with open(cache_path, 'wb') as f:
            f.write(pdf_content)
        print(f"Cached PDF for route {route_code} at {cache_path}")
    except Exception as e:
        print(f"Error caching PDF: {e}")


async def download_route_pdf(route_code: str, use_cache: bool = True) -> bytes | None:
    """Download the PDF timetable for a specific bus route.

    Args:
        route_code: The route code to download
        use_cache: Whether to use cached PDF if available (default: True)
    """
    route_code = route_code.upper()

    # Check cache first
    if use_cache:
        cached_pdf = get_cached_pdf(route_code)
        if cached_pdf:
            print(f"Using cached PDF for route {route_code}")
            return cached_pdf

    route_info = KNOWN_ROUTES.get(route_code)

    if not route_info:
        return None

    url = f"{RTA_API_BASE}?lineId={route_info['lineId']}&lineName={route_info['lineName']}"
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/pdf"
    }

    async with httpx.AsyncClient(follow_redirects=True, verify=False) as client:
        try:
            print(f"Downloading PDF for route {route_code} from RTA API...")
            response = await client.get(url, headers=headers, timeout=90.0)
            response.raise_for_status()

            # Check if response is actually a PDF
            content_type = response.headers.get('content-type', '')

            # Save response for debugging
            pdf_content = response.content

            if len(pdf_content) < 100:
                print(f"Warning: Response too small ({len(pdf_content)} bytes). Might not be a valid PDF.")
                print(f"Content preview: {pdf_content[:100]}")
                return None

            if 'pdf' not in content_type.lower() and not pdf_content.startswith(b'%PDF'):
                print(f"Warning: Response might not be a PDF. Content-Type: {content_type}")
                print(f"First bytes: {pdf_content[:50]}")

            # Cache the PDF
            save_pdf_to_cache(route_code, pdf_content)

            return pdf_content
        except httpx.TimeoutException as e:
            print(f"Timeout downloading PDF for route {route_code}: {e}")
            return None
        except httpx.HTTPStatusError as e:
            print(f"HTTP error downloading PDF for route {route_code}: {e.response.status_code} - {e.response.text[:200]}")
            return None
        except Exception as e:
            print(f"Error downloading PDF for route {route_code}: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return None


def parse_time(time_str: str) -> time | None:
    """Parse a time string in various formats to a time object."""
    if not time_str or not isinstance(time_str, str):
        return None

    time_str = time_str.strip()

    # Common time formats
    patterns = [
        r'^(\d{1,2}):(\d{2})$',  # HH:MM or H:MM
        r'^(\d{1,2})\.(\d{2})$',  # HH.MM or H.MM
        r'^(\d{1,2})(\d{2})$',    # HHMM or HMM
    ]

    for pattern in patterns:
        match = re.match(pattern, time_str)
        if match:
            try:
                hour = int(match.group(1))
                minute = int(match.group(2))

                # Handle 24-hour format
                if hour >= 24:
                    hour = hour % 24

                if 0 <= hour < 24 and 0 <= minute < 60:
                    return time(hour, minute)
            except (ValueError, IndexError):
                continue

    return None


def extract_schedule_from_pdf(pdf_content: bytes, route_code: str) -> dict[str, Any]:
    """Extract schedule information from PDF timetable."""
    if not pdfplumber:
        return {
            "error": "PDF parsing library not available. Install pdfplumber: pip install pdfplumber",
            "route": route_code
        }

    try:
        schedule_data = {
            "route": route_code,
            "stops": [],
            "times": [],
            "raw_text": "",
            "parsed": False
        }

        with pdfplumber.open(io.BytesIO(pdf_content)) as pdf:
            all_text = []

            for page_num, page in enumerate(pdf.pages):
                # Extract text
                text = page.extract_text()
                if text:
                    all_text.append(f"--- Page {page_num + 1} ---\n{text}")

                # Try to extract tables
                tables = page.extract_tables()
                if tables:
                    for table_idx, table in enumerate(tables):
                        if table and len(table) > 0:
                            # First row might be headers (stop names)
                            headers = table[0] if table else []

                            # Process time rows
                            for row in table[1:]:
                                if row and any(cell for cell in row if cell):
                                    # Filter out empty cells and try to parse times
                                    times = []
                                    for cell in row:
                                        parsed_time = parse_time(str(cell)) if cell else None
                                        if parsed_time:
                                            times.append(parsed_time.strftime("%H:%M"))

                                    if times:
                                        schedule_data["times"].append(times)

                            # Store stop names from headers
                            if headers and not schedule_data["stops"]:
                                schedule_data["stops"] = [str(h).strip() for h in headers if h and str(h).strip()]

            schedule_data["raw_text"] = "\n\n".join(all_text)
            schedule_data["parsed"] = bool(schedule_data["times"] or schedule_data["raw_text"])

        return schedule_data

    except Exception as e:
        return {
            "error": f"Failed to parse PDF: {str(e)}",
            "route": route_code
        }


def find_next_departure(schedule_data: dict, requested_time: str) -> str:
    """Find the next bus departure after the requested time."""
    if "error" in schedule_data:
        return f"Error: {schedule_data['error']}"

    if not schedule_data.get("times"):
        return "No schedule times found in the timetable. Raw content available in full schedule."

    req_time = parse_time(requested_time)
    if not req_time:
        return f"Invalid time format: {requested_time}. Please use HH:MM format."

    # Convert all departure times and find the next one
    next_departures = []

    for time_row in schedule_data["times"]:
        for time_str in time_row:
            dep_time = parse_time(time_str)
            if dep_time and dep_time >= req_time:
                next_departures.append((dep_time, time_str))

    if not next_departures:
        return f"No departures found after {requested_time} for route {schedule_data['route']}"

    # Sort and get the earliest
    next_departures.sort(key=lambda x: x[0])

    result = [f"Next departures for Route {schedule_data['route']} after {requested_time}:\n"]

    # Show up to 5 next departures
    for dep_time, time_str in next_departures[:5]:
        time_diff = (datetime.combine(datetime.today(), dep_time) -
                    datetime.combine(datetime.today(), req_time))
        minutes = int(time_diff.total_seconds() / 60)
        result.append(f"  {time_str} (in {minutes} minutes)")

    if schedule_data.get("stops"):
        result.append(f"\nStops: {', '.join(schedule_data['stops'][:5])}")
        if len(schedule_data['stops']) > 5:
            result.append(f" ... and {len(schedule_data['stops']) - 5} more")

    return "\n".join(result)


@mcp.tool()
async def get_available_routes() -> str:
    """Get a list of available Dubai bus routes that can be queried.

    Returns a list of known bus routes with their route codes.
    """
    result = ["Available RTA Dubai Bus Routes:\n"]
    result.append("=" * 50)

    for route_code in sorted(KNOWN_ROUTES.keys()):
        result.append(f"  Route {route_code}")

    result.append("\n" + "=" * 50)
    result.append("\nTo get the schedule for a route, use get_route_schedule(route_code)")
    result.append("To find next bus, use find_next_bus(route_code, time)")

    return "\n".join(result)


@mcp.tool()
async def get_route_schedule(route_code: str) -> str:
    """Download and display the full schedule for a specific bus route.

    Args:
        route_code: The bus route code (e.g., "SH1", "D03", "E411", "F62", "8", "11", "C01", "C10")
    """
    route_code = route_code.upper().strip()

    if route_code not in KNOWN_ROUTES:
        available = ", ".join(sorted(KNOWN_ROUTES.keys()))
        return f"Route {route_code} not found. Available routes: {available}"

    pdf_content = await download_route_pdf(route_code)

    if not pdf_content:
        return f"Failed to download timetable for route {route_code}"

    schedule = extract_schedule_from_pdf(pdf_content, route_code)

    if "error" in schedule:
        return f"Error processing timetable: {schedule['error']}"

    result = [f"Route {route_code} Schedule"]
    result.append("=" * 60)

    if schedule.get("stops"):
        result.append(f"\nStops ({len(schedule['stops'])}):")
        for i, stop in enumerate(schedule['stops'][:10], 1):
            result.append(f"  {i}. {stop}")
        if len(schedule['stops']) > 10:
            result.append(f"  ... and {len(schedule['stops']) - 10} more stops")

    if schedule.get("times"):
        result.append(f"\n\nSchedule Times (showing first 10 departures):")
        for i, time_row in enumerate(schedule['times'][:10], 1):
            times_str = " → ".join(time_row[:5])
            if len(time_row) > 5:
                times_str += f" ... (+{len(time_row) - 5} more)"
            result.append(f"  {i}. {times_str}")

    if schedule.get("raw_text") and not schedule.get("times"):
        result.append("\n\nRaw Timetable Content (first 1500 characters):")
        result.append("-" * 60)
        result.append(schedule['raw_text'][:1500])
        if len(schedule['raw_text']) > 1500:
            result.append("\n... (content truncated)")

    result.append("\n" + "=" * 60)
    result.append(f"\nPDF Size: {len(pdf_content)} bytes")
    result.append(f"Use find_next_bus('{route_code}', 'HH:MM') to find next departure")

    return "\n".join(result)


@mcp.tool()
async def find_next_bus(route_code: str, departure_time: str) -> str:
    """Find the next bus departure for a route after a specified time.

    Args:
        route_code: The bus route code (e.g., "SH1", "D03", "E411")
        departure_time: Time in HH:MM format (24-hour, e.g., "14:30", "09:00")
    """
    route_code = route_code.upper().strip()

    if route_code not in KNOWN_ROUTES:
        available = ", ".join(sorted(KNOWN_ROUTES.keys()))
        return f"Route {route_code} not found. Available routes: {available}"

    pdf_content = await download_route_pdf(route_code)

    if not pdf_content:
        return f"Failed to download timetable for route {route_code}"

    schedule = extract_schedule_from_pdf(pdf_content, route_code)

    return find_next_departure(schedule, departure_time)


@mcp.tool()
async def add_custom_route(route_code: str, line_id: str, line_name: str) -> str:
    """Add a custom bus route to the available routes.

    Args:
        route_code: Short route identifier (e.g., "X28")
        line_id: Full RTA line ID (e.g., "dub:01X28:%20:H:y08")
        line_name: URL-encoded line name (e.g., "bus%20X28")
    """
    route_code = route_code.upper().strip()

    KNOWN_ROUTES[route_code] = {
        "lineId": line_id,
        "lineName": line_name
    }

    return f"Successfully added route {route_code}. You can now query it using get_route_schedule or find_next_bus."


@mcp.tool()
async def get_cache_status() -> str:
    """Get information about cached PDF timetables.

    Returns information about which routes have cached PDFs and cache size.
    """
    result = ["PDF Cache Status\n"]
    result.append("=" * 60)
    result.append(f"Cache Directory: {CACHE_DIR}\n")

    if not CACHE_DIR.exists():
        result.append("Cache directory does not exist.")
        return "\n".join(result)

    cached_files = list(CACHE_DIR.glob("*.pdf"))

    if not cached_files:
        result.append("No cached PDFs found.")
    else:
        result.append(f"Cached Routes ({len(cached_files)}):\n")

        total_size = 0
        for cache_file in sorted(cached_files):
            size = cache_file.stat().st_size
            total_size += size
            route_name = cache_file.stem
            result.append(f"  {route_name}: {size:,} bytes ({size / 1024:.1f} KB)")

        result.append(f"\nTotal Cache Size: {total_size:,} bytes ({total_size / 1024:.1f} KB)")

    result.append("\nUse clear_cache() to remove all cached PDFs")

    return "\n".join(result)


@mcp.tool()
async def clear_cache(route_code: Optional[str] = None) -> str:
    """Clear cached PDF timetables.

    Args:
        route_code: Optional route code to clear specific cache. If not provided, clears all cache.
    """
    if route_code:
        route_code = route_code.upper().strip()
        cache_path = get_cache_path(route_code)

        if cache_path.exists():
            try:
                cache_path.unlink()
                return f"Successfully cleared cache for route {route_code}"
            except Exception as e:
                return f"Error clearing cache for route {route_code}: {e}"
        else:
            return f"No cached PDF found for route {route_code}"
    else:
        # Clear all cache
        try:
            cached_files = list(CACHE_DIR.glob("*.pdf"))
            count = len(cached_files)

            for cache_file in cached_files:
                cache_file.unlink()

            return f"Successfully cleared cache for {count} route(s)"
        except Exception as e:
            return f"Error clearing cache: {e}"


@mcp.tool()
async def import_pdf_timetable(route_code: str, pdf_path: str) -> str:
    """Import a PDF timetable from a local file into the cache.

    Use this when the RTA API is not accessible or when you have manually downloaded timetables.

    Args:
        route_code: The route code this PDF belongs to (e.g., "SH1", "D03")
        pdf_path: Path to the PDF file on your local system
    """
    route_code = route_code.upper().strip()

    # Check if the file exists
    pdf_file = Path(pdf_path)
    if not pdf_file.exists():
        return f"Error: PDF file not found at {pdf_path}"

    # Read the PDF
    try:
        with open(pdf_file, 'rb') as f:
            pdf_content = f.read()

        # Verify it's a PDF
        if not pdf_content.startswith(b'%PDF'):
            return f"Error: File at {pdf_path} does not appear to be a valid PDF"

        # Save to cache
        save_pdf_to_cache(route_code, pdf_content)

        # Add route to KNOWN_ROUTES if not already there
        if route_code not in KNOWN_ROUTES:
            KNOWN_ROUTES[route_code] = {
                "lineId": f"dub:01{route_code}:%20:H:y08",
                "lineName": f"bus%20{route_code}"
            }

        return f"Successfully imported PDF timetable for route {route_code} ({len(pdf_content)} bytes)\nYou can now use get_route_schedule('{route_code}') or find_next_bus('{route_code}', 'HH:MM')"

    except Exception as e:
        return f"Error importing PDF: {e}"


if __name__ == "__main__":
    mcp.run(transport='sse')
