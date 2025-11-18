# Dubai Transport MCP Server

This MCP server provides access to RTA Dubai bus journey planning through PDF timetable parsing and schedule extraction.

## Features

- **Bus Route Schedules**: Download and parse PDF timetables for Dubai RTA bus routes
- **Next Bus Finder**: Find the next bus departure for a specific route at a given time
- **Route Management**: List available routes and add custom routes
- **PDF Parsing**: Automatic extraction of schedules from RTA PDF timetables
- **No API Key Required**: Uses the public RTA Dubai API

## Prerequisites

- Python 3.11+
- httpx
- mcp
- pdfplumber

## Installation

### Setup a venv

```bash
python3.11 -m venv venv
source venv/bin/activate
```

### Install dependencies

```bash
pip install -e .
```

## Usage

### Run MCP Server

Note: runs on port 8000 by default

```bash
python dubai_transport.py
```

## Available Tools

### get_available_routes
Get a list of available Dubai bus routes that can be queried.

**Returns:** List of known bus routes with their route codes.

**Example routes:**
- SH1: Sheikh Mohammed Bin Zayed Road route
- D03: Downtown Dubai route
- E411: Emirates Road route
- F62: Al Fahidi route
- 8, 11: Numbered routes
- C01, C10: City routes

### get_route_schedule
Download and display the full schedule for a specific bus route.

**Parameters:**
- `route_code` (str): The bus route code (e.g., "SH1", "D03", "E411", "F62")

**Returns:** Complete schedule with stops and departure times extracted from PDF timetable.

**Example:**
```python
await get_route_schedule("SH1")
```

### find_next_bus
Find the next bus departure for a route after a specified time.

**Parameters:**
- `route_code` (str): The bus route code (e.g., "SH1", "D03", "E411")
- `departure_time` (str): Time in HH:MM format (24-hour, e.g., "14:30", "09:00")

**Returns:** Next available departures with countdown times.

**Example:**
```python
await find_next_bus("D03", "14:30")
```

### add_custom_route
Add a custom bus route to the available routes.

**Parameters:**
- `route_code` (str): Short route identifier (e.g., "X28")
- `line_id` (str): Full RTA line ID (e.g., "dub:01X28:%20:H:y08")
- `line_name` (str): URL-encoded line name (e.g., "bus%20X28")

**Example:**
```python
await add_custom_route("X28", "dub:01X28:%20:H:y08", "bus%20X28")
```

### get_cache_status
Get information about cached PDF timetables.

**Returns:** Information about which routes have cached PDFs and cache size.

**Example:**
```python
await get_cache_status()
```

### clear_cache
Clear cached PDF timetables.

**Parameters:**
- `route_code` (str, optional): Route code to clear specific cache. If not provided, clears all cache.

**Example:**
```python
# Clear specific route
await clear_cache("SH1")

# Clear all cache
await clear_cache()
```

### import_pdf_timetable
Import a PDF timetable from a local file into the cache.

Use this when the RTA API is not accessible or when you have manually downloaded timetables.

**Parameters:**
- `route_code` (str): The route code this PDF belongs to (e.g., "SH1", "D03")
- `pdf_path` (str): Path to the PDF file on your local system

**Example:**
```python
await import_pdf_timetable("SH1", "/path/to/SH1_timetable.pdf")
```

## Examples

### Getting available routes
```python
# List all available routes
result = await get_available_routes()
```

### Viewing a route schedule
```python
# Get full schedule for route SH1
result = await get_route_schedule("SH1")
```

### Finding next bus
```python
# Find next bus on route D03 after 2:30 PM
result = await find_next_bus("D03", "14:30")

# Find morning bus on route E411
result = await find_next_bus("E411", "08:00")
```

## Integration with Llama Stack

### Review Tools

First check which tools are already registered:

```bash
LLAMA_STACK_ENDPOINT=http://localhost:8321
curl -sS $LLAMA_STACK_ENDPOINT/v1/toolgroups -H "Content-Type: application/json" | jq
```

### Register the Dubai transport MCP server

If running Llama Stack in a container:

```bash
curl -X POST -H "Content-Type: application/json" \
  --data '{
    "provider_id": "model-context-protocol",
    "toolgroup_id": "mcp::dubai-transport",
    "mcp_endpoint": {
      "uri": "http://host.docker.internal:8000/sse"
    }
  }' \
  $LLAMA_STACK_ENDPOINT/v1/toolgroups
```

If running Llama Stack locally:

```bash
curl -X POST -H "Content-Type: application/json" \
  --data '{
    "provider_id": "model-context-protocol",
    "toolgroup_id": "mcp::dubai-transport",
    "mcp_endpoint": {
      "uri": "http://localhost:8000/sse"
    }
  }' \
  $LLAMA_STACK_ENDPOINT/v1/toolgroups
```

### Check registration

```bash
curl -sS $LLAMA_STACK_ENDPOINT/v1/toolgroups -H "Content-Type: application/json" | jq
```

### Test connectivity

```bash
export LLAMA_STACK_MODEL=meta-llama/Llama-3.2-3B-Instruct
# or
export LLAMA_STACK_MODEL=meta-llama/Llama-3.1-8B-Instruct

API_KEY=none
LLAMA_STACK_ENDPOINT=http://localhost:8321

curl -sS $LLAMA_STACK_ENDPOINT/v1/inference/chat-completion \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY" \
  -d "{
     \"model_id\": \"$LLAMA_STACK_MODEL\",
     \"messages\": [{\"role\": \"user\", \"content\": \"what model are you?\"}],
     \"temperature\": 0.0
   }" | jq -r '.completion_message | select(.role == "assistant") | .content'
```

### Run tests

```bash
python test_dubai_transport.py
```

## Data Features

The server provides comprehensive information including:
- **PDF Timetable Downloads**: Automatic download of official RTA timetables
- **Schedule Extraction**: Parse and extract departure times from PDF documents
- **Stop Information**: List of all stops along the route
- **Time Calculations**: Find next departures with countdown timers
- **Multiple Route Support**: Pre-configured common routes with extensibility
- **Custom Route Addition**: Add new routes dynamically

## Technical Details

### PDF Parsing

The server uses `pdfplumber` to extract schedule information from RTA PDF timetables. The parsing handles:
- Table extraction for structured timetables
- Text extraction for unstructured content
- Time parsing in multiple formats (HH:MM, HH.MM, HHMM)
- Stop name extraction from table headers

### Time Zones

All times are in Gulf Standard Time (GST/UTC+4), which is Dubai's local timezone.

### Route ID Format

RTA route IDs follow the pattern: `dub:{code}:%20:H:y08`
- Example: `dub:01SH1:%20:H:y08` for route SH1

## API Reference

This server uses the RTA Dubai Journey Planner API:
- Base URL: https://www.rta.ae/wps/PA_JourneyPlanner/DownloadTimetableServlet
- Documentation: https://rtadubaiapi.readthedocs.io/
- Data format: PDF timetables
- No authentication required

## Troubleshooting

### API Access Issues

**Important:** The RTA Dubai API may not be accessible from all geographic locations. If you experience timeouts or connection issues:

1. **Manual PDF Download Option:**
   - Visit the RTA Dubai website: https://www.rta.ae/
   - Navigate to journey planner or bus schedule section
   - Download the PDF timetables for your desired routes
   - Use the `import_pdf_timetable()` tool to import them:
     ```python
     await import_pdf_timetable("SH1", "/path/to/downloaded/SH1.pdf")
     ```

2. **Using the Cache:**
   - Once a PDF is imported or successfully downloaded, it's cached locally
   - Subsequent queries use the cached version (no internet required)
   - Check cache status: `await get_cache_status()`
   - Cache location: `~/.cache/dubai-transport-mcp/`

### PDF Parsing Issues

If schedule times are not being extracted:
1. Check the raw text output in the schedule response
2. PDF formats may vary - some may require manual interpretation
3. Ensure `pdfplumber` is installed: `pip install pdfplumber`
4. Some PDFs may have complex layouts that require adjustments to parsing logic

### Route Not Found

To add a new route:
1. Find the route on RTA Dubai website
2. Determine the line ID format (follow existing patterns)
3. Option 1: Use `add_custom_route` tool to register it
4. Option 2: Download the PDF manually and use `import_pdf_timetable`

### Connection Timeouts

PDF downloads may take time or timeout:
- Default timeout is 90 seconds
- API may have geographic restrictions
- If downloads fail repeatedly, use manual PDF import method
- Check if you're behind a firewall or proxy

## Cache Management

The server uses a local cache to store downloaded PDF timetables:

- **Cache Location:** `~/.cache/dubai-transport-mcp/`
- **Cache Benefits:**
  - Faster subsequent queries
  - Works offline after initial download/import
  - Reduces load on RTA servers
- **Cache Tools:**
  - `get_cache_status()` - View cached routes
  - `clear_cache()` - Remove all cached PDFs
  - `clear_cache(route_code)` - Remove specific route cache
  - `import_pdf_timetable()` - Manually add PDFs to cache

## Manual PDF Import Workflow

If the RTA API is not accessible:

1. **Download PDF from RTA Website:**
   - Go to https://www.rta.ae/
   - Find the journey planner or timetable section
   - Download PDF for your route (e.g., SH1, D03, etc.)

2. **Import to MCP Server:**
   ```python
   await import_pdf_timetable("SH1", "/downloads/SH1_schedule.pdf")
   ```

3. **Query the Schedule:**
   ```python
   # View full schedule
   await get_route_schedule("SH1")

   # Find next bus
   await find_next_bus("SH1", "14:30")
   ```

## Contributing

To add more routes, update the `KNOWN_ROUTES` dictionary in `dubai_transport.py` with the correct line ID and line name from the RTA API.