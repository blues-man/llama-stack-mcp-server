# Dubai Transport MCP Server - Quick Setup Guide

This guide will help you get started with the Dubai Transport MCP Server.

## What Was Created

Based on the Vienna public transportation MCP server template, a new Dubai RTA Bus Journey Planner MCP server with the following features:

### Core Files

1. **dubai_transport.py** - Main MCP server implementation
2. **test_dubai_transport.py** - Test suite
3. **README.md** - Comprehensive documentation
4. **pyproject.toml** - Python package configuration
5. **Containerfile** - Docker container definition

### Features Implemented

#### MCP Tools (7 total)

1. **get_available_routes** - List all available bus routes
2. **get_route_schedule** - Download and parse PDF timetable for a route
3. **find_next_bus** - Find next bus departure after a specified time
4. **add_custom_route** - Add new routes dynamically
5. **get_cache_status** - View cached PDF information
6. **clear_cache** - Remove cached PDFs
7. **import_pdf_timetable** - Import manually downloaded PDFs

#### Key Features

- **PDF Parsing:** Automatic extraction of schedules from RTA PDF timetables using pdfplumber
- **Smart Caching:** Local cache system to avoid repeated downloads
- **Time Parsing:** Flexible time format support (HH:MM, HH.MM, HHMM)
- **Offline Support:** Works offline once PDFs are cached
- **Manual Import:** Fallback for when API is not accessible

## Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install packages
pip install -e .
```

### 2. Run the Server

```bash
python dubai_transport.py
```

The server will start on port 8000 by default.

### 3. Test the Tools

```bash
# Test basic functionality
python -c "
import asyncio
from dubai_transport import get_available_routes

print(asyncio.run(get_available_routes()))
"
```

## Working with the RTA API

### Important Note: API Accessibility

The RTA Dubai API may not be accessible from all locations due to:
- Geographic restrictions
- Network firewalls
- API availability

### Recommended Workflow

#### Option 1: Direct API (if accessible)

```python
# The server will attempt to download PDFs directly
await get_route_schedule("SH1")
```

#### Option 2: Manual PDF Import (recommended)

1. Download PDF timetables from https://www.rta.ae/
2. Import them into the server:

```python
await import_pdf_timetable("SH1", "/path/to/SH1.pdf")
```

3. Query the schedule:

```python
# View full schedule
await get_route_schedule("SH1")

# Find next bus at 2:30 PM
await find_next_bus("SH1", "14:30")
```

## Available Routes

Pre-configured routes include:
- **SH1** - Sheikh Mohammed Bin Zayed Road
- **D03** - Downtown Dubai
- **E411** - Emirates Road
- **F62** - Al Fahidi
- **8, 11** - Numbered routes
- **C01, C10** - City routes

## Cache Management

### View Cache

```python
await get_cache_status()
```

### Clear Cache

```python
# Clear all
await clear_cache()

# Clear specific route
await clear_cache("SH1")
```

### Cache Location

PDFs are cached at: `~/.cache/dubai-transport-mcp/`

## Integration with Llama Stack

### Register the Server

```bash
LLAMA_STACK_ENDPOINT=http://localhost:8321

# If Llama Stack is in a container
curl -X POST -H "Content-Type: application/json" \
  --data '{
    "provider_id": "model-context-protocol",
    "toolgroup_id": "mcp::dubai-transport",
    "mcp_endpoint": {
      "uri": "http://host.docker.internal:8000/sse"
    }
  }' \
  $LLAMA_STACK_ENDPOINT/v1/toolgroups

# If Llama Stack is local
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

### Verify Registration

```bash
curl -sS $LLAMA_STACK_ENDPOINT/v1/toolgroups -H "Content-Type: application/json" | jq
```

## Example Queries for AI Agents

Once integrated with Llama Stack, you can ask natural language questions like:

- "What bus routes are available in Dubai?"
- "When is the next SH1 bus after 3pm?"
- "Show me the full schedule for route D03"
- "What routes go through Downtown Dubai?"

## Troubleshooting

### PDF Download Fails

**Solution:** Use manual PDF import
```python
await import_pdf_timetable("ROUTE_CODE", "/path/to/pdf")
```

### Schedule Times Not Extracted

**Possible causes:**
- PDF format is complex
- Tables not in expected format

**Solution:** Check raw text output and potentially adjust parsing logic

### Cache Not Working

**Check:**
```python
await get_cache_status()
```

**Clear and retry:**
```python
await clear_cache()
```

## Development

### Running Tests

```bash
python test_dubai_transport.py
```

### Adding New Routes

```python
await add_custom_route(
    "X28",
    "dub:01X28:%20:H:y08",
    "bus%20X28"
)
```

## Architecture

```
dubai_transport.py
├── FastMCP Server (port 8000)
├── PDF Download (with caching)
├── PDF Parsing (pdfplumber)
├── Schedule Extraction
└── Time Calculation
```

### Data Flow

1. User requests schedule → 2. Check cache → 3. Download PDF (if needed) → 4. Parse PDF → 5. Extract schedule → 6. Return formatted results

## Next Steps

1. Test the basic tools (get_available_routes, get_cache_status)
2. Download a sample PDF from RTA website
3. Import it using import_pdf_timetable
4. Test schedule queries
5. Integrate with Llama Stack
6. Query using natural language through AI agent

## Support

For issues or questions:
- Check the main README.md for detailed documentation
- Review the Troubleshooting section
- Examine the source code in dubai_transport.py

## Differences from Vienna Template

| Feature | Vienna | Dubai |
|---------|--------|-------|
| Data Source | Real-time JSON API | PDF Timetables |
| Parsing | JSON parsing | PDF extraction |
| Caching | Not implemented | Full cache system |
| Offline | No | Yes (with cache) |
| Manual Import | No | Yes |
| Data Type | Live departures | Static schedules |
