# Riyadh Transport MCP Server

This MCP server provides access to Riyadh public transportation data through the RCRC (Riyadh Public Transport Company) open data API.

## Features

- **Bus Route Search**: Search for bus routes by various criteria (route number, origin, destination)
- **Route Details**: Get detailed information about specific bus routes including GPS waypoints
- **Area-based Search**: Find all bus routes serving a specific area or neighborhood
- **Route Listing**: Browse all available bus routes in Riyadh
- **Multilingual Support**: Display route information in both English and Arabic
- **No API Key Required**: Uses the free RCRC open data API

## Prerequisites

- Python 3.11+
- httpx
- mcp

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

Note: runs on 8000 by default

```bash
python riyadh_transport.py
```

## Available Tools

### search_bus_routes
Search for bus routes by various criteria.

**Parameters:**
- `query` (str, optional): General search query for route information
- `route_number` (str, optional): Specific bus route number to search for
- `origin` (str, optional): Search by origin location
- `destination` (str, optional): Search by destination location
- `limit` (int, optional): Maximum number of results to return (default: 10)

### get_route_details
Get detailed information about a specific bus route by its route code.

**Parameters:**
- `route_code` (str): The bus route code (e.g., "L19-1")

### list_all_routes
List all available bus routes in Riyadh.

**Parameters:**
- `limit` (int, optional): Maximum number of routes to return (default: 20)

### search_routes_by_area
Search for bus routes that serve a specific area or neighborhood in Riyadh.

**Parameters:**
- `area_name` (str): Name of the area or neighborhood to search for
- `limit` (int, optional): Maximum number of routes to return (default: 10)

## Examples

### Searching for routes
```python
# Search by route number
await search_bus_routes(route_number="19")

# Search by origin
await search_bus_routes(origin="King Khalid Airport")

# Search by destination
await search_bus_routes(destination="Riyadh Station")

# General search
await search_bus_routes(query="University")
```

### Getting route details
```python
# Get detailed information about a specific route
await get_route_details("L19-1")
```

### Finding routes by area
```python
# Find all routes serving a specific area
await search_routes_by_area("Olaya")
```

## Data Features

The server provides rich information including:
- **Route codes and numbers** for easy identification
- **Multilingual support** (English and Arabic names)
- **Geographic information** including GPS coordinates and route waypoints
- **Direction information** for different route directions
- **Complete route mapping** with start and end points
- **Route comments** in both languages

## Integration with Llama Stack

### Review Tools

First check to see which tools are already registered

```bash
LLAMA_STACK_ENDPOINT=http://localhost:8321
curl -sS $LLAMA_STACK_ENDPOINT/v1/toolgroups -H "Content-Type: application/json" | jq
```

### Register the Riyadh transport MCP server

If running Llama Stack in a container:

```bash
curl -X POST -H "Content-Type: application/json" --data '{ "provider_id" : "model-context-protocol", "toolgroup_id" : "mcp::riyadh-transport", "mcp_endpoint" : { "uri" : "http://host.docker.internal:8000/sse"}}' $LLAMA_STACK_ENDPOINT/v1/toolgroups
```

Else:

```bash
curl -X POST -H "Content-Type: application/json" --data '{ "provider_id" : "model-context-protocol", "toolgroup_id" : "mcp::riyadh-transport", "mcp_endpoint" : { "uri" : "http://localhost:8000/sse"}}' $LLAMA_STACK_ENDPOINT/v1/toolgroups
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
```

```bash
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

And test the Riyadh transport tool invocation via a Llama Stack Client

```bash
python test_riyadh_transport.py
```

## API Reference

This server uses the RCRC (Riyadh Public Transport Company) open data API:
- Base URL: https://opendata.rcrc.gov.sa/api/explore/v2.1/catalog/datasets/
- Dataset: bus-roads-by-direction-in-riyadh-2024
- Data format: JSON with detailed route and geographic information
- No authentication required

## Route Information

The API provides access to Riyadh's comprehensive bus network including:
- Regular bus routes throughout the city
- Route directions and GPS tracking
- Multilingual route information (English/Arabic)
- Geographic waypoints for precise route mapping
- Origin and destination information

## Sample Routes

Some example routes available in the system:
- **L19-1**: Transportation Center → King Saud University
- **L11-1**: West Al-Uraija → Ar Rabi
- **L13-1**: As-Sulaimanyah → National Guard Hospital
- **L46-1**: Riyadh Exhibition Center → Al Arid