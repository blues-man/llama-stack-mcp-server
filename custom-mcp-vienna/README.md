# Vienna Transport MCP Server

This MCP server provides access to Vienna public transportation data through the Wiener Linien real-time API.

## Features

- **Real-time Station Monitor**: Get live departure information for Vienna public transport stations
- **Multiple Station Monitoring**: Monitor multiple stations simultaneously
- **Station Search Guidance**: Help finding RBL numbers for Vienna stations
- **No API Key Required**: Uses the free Wiener Linien open data API

## Prerequisites

- Python 3.11+
- httpx
- mcp

## Installation

### Setup a venv

```
python3.11 -m venv venv
source venv/bin/activate
```

### Install dependencies

```
pip install -e .
```

## Usage

### Run MCP Server

Note: runs on 8000 by default

```
python vienna_transport.py
```

## Available Tools

### get_station_monitor
Get real-time public transportation departures for a Vienna station using RBL number.

**Parameters:**
- `rbl` (str): RBL (Rechnergestütztes Betriebsleitsystem) number for the station

**Example RBL numbers:**
- 4127: Kagran U1 station
- 4201: Stephansplatz U1
- 4205: Karlsplatz U1
- 4202: Schwedenplatz U1
- 4301: Westbahnhof U3
- 4021: Schottentor U2

### get_multiple_stations_monitor
Get real-time departures for multiple Vienna stations using comma-separated RBL numbers.

**Parameters:**
- `rbl_list` (str): Comma-separated list of RBL numbers (e.g., "4127,4128,4129")

### search_vienna_stations
Search for Vienna public transport stations by name and get guidance on finding RBL numbers.

**Parameters:**
- `name` (str): Station name to search for

## Examples

### Getting station departures
```python
# Get real-time departures for Kagran U1 station
await get_station_monitor("4127")

# Monitor multiple stations
await get_multiple_stations_monitor("4127,4201,4205")
```

### Finding station information
```python
# Search for information about a station
await search_vienna_stations("Stephansplatz")
```

## Integration with Llama Stack

### Review Tools

First check to see which tools are already registered

```
LLAMA_STACK_ENDPOINT=http://localhost:8321
curl -sS $LLAMA_STACK_ENDPOINT/v1/toolgroups -H "Content-Type: application/json" | jq
```

### Register the Vienna transport MCP server

If running Llama Stack in a container

```
curl -X POST -H "Content-Type: application/json" --data '{ "provider_id" : "model-context-protocol", "toolgroup_id" : "mcp::vienna-transport", "mcp_endpoint" : { "uri" : "http://host.docker.internal:8000/sse"}}' $LLAMA_STACK_ENDPOINT/v1/toolgroups
```

Else

```
curl -X POST -H "Content-Type: application/json" --data '{ "provider_id" : "model-context-protocol", "toolgroup_id" : "mcp::vienna-transport", "mcp_endpoint" : { "uri" : "http://localhost:8000/sse"}}' $LLAMA_STACK_ENDPOINT/v1/toolgroups
```

### Check registration

```
curl -sS $LLAMA_STACK_ENDPOINT/v1/toolgroups -H "Content-Type: application/json" | jq
```

### Test connectivity

```
export LLAMA_STACK_MODEL=meta-llama/Llama-3.2-3B-Instruct
# or
export LLAMA_STACK_MODEL=meta-llama/Llama-3.1-8B-Instruct
```

```
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

And test the Vienna transport tool invocation via a Llama Stack Client

```
python test_vienna_transport.py
```

## Data Features

The server provides rich information including:
- **Real-time departures** with countdown timers
- **Platform information** and directions
- **Accessibility features** (barrier-free access, folding ramps)
- **Service disruptions** and traffic jam indicators
- **Multiple transport types** (U-Bahn, Straßenbahn, Bus)
- **Live vs. scheduled times** with delay information

## API Reference

This server uses the Wiener Linien Open Data real-time API:
- Base URL: https://www.wienerlinien.at/ogd_realtime/
- Documentation: Available on the Wiener Linien website
- Data format: JSON with detailed departure and vehicle information