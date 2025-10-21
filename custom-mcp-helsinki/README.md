## Helsinki Transport MCP Server

MCP server for Helsinki public transportation data using Digitransit GraphQL API.

## Local Development and Testing

### Setup a venv

```bash
python3.11 -m venv venv
source venv/bin/activate
```

### Set the API key

```bash
export DIGITRANSIT_API_KEY="7362abc5ea0a45f4805cda7238143a0a"
```

### Install dependencies

```bash
pip install fastmcp==2.2.2
```

### Run MCP Server

Note: runs on port 8000 by default

```bash
python helsinki_transport.py
```

### Test the server

```bash
python test_helsinki_transport.py
```

## Available Tools

The server provides the following tools:

- `get_departures`: Get real-time departures from a Helsinki stop (default: HSL:1040129 - Arkadian puisto)
- `get_timetable`: Get timetable for a stop within a specific time range
- `get_stop_info`: Get detailed information about a specific stop

## API Information

- **API URL**: https://api.digitransit.fi/routing/v2/hsl/gtfs/v1
- **API Key**: digitransit-subscription-key header
- **Default Stop ID**: HSL:1040129 (Arkadian puisto, Helsinki)
- **GraphiQL Explorer**: https://api.digitransit.fi/graphiql/hsl/v2/gtfs/v1
- **Documentation**: https://digitransit.fi/en/developers/apis/1-routing-api/

## Llama Stack Integration

### Review Tools

First check to see which tools are already registered:

```bash
LLAMA_STACK_ENDPOINT=http://localhost:8321
curl -sS $LLAMA_STACK_ENDPOINT/v1/toolgroups -H "Content-Type: application/json" | jq
```

### Register the Helsinki Transport MCP server

If running Llama Stack in a container:

```bash
curl -X POST -H "Content-Type: application/json" --data '{ "provider_id" : "model-context-protocol", "toolgroup_id" : "mcp::helsinki-transport", "mcp_endpoint" : { "uri" : "http://host.docker.internal:8000/sse"}}' $LLAMA_STACK_ENDPOINT/v1/toolgroups
```

Else:

```bash
curl -X POST -H "Content-Type: application/json" --data '{ "provider_id" : "model-context-protocol", "toolgroup_id" : "mcp::helsinki-transport", "mcp_endpoint" : { "uri" : "http://localhost:8000/sse"}}' $LLAMA_STACK_ENDPOINT/v1/toolgroups
```

### Check registration

```bash
curl -sS $LLAMA_STACK_ENDPOINT/v1/toolgroups -H "Content-Type: application/json" | jq
```

### Test connectivity

Register the 8B model for better tool calling:

```bash
curl -sS $LLAMA_STACK_ENDPOINT/v1/models -H "Content-Type: application/json" | jq -r '.data[].identifier'
```

Set the model:

```bash
export LLAMA_STACK_MODEL=meta-llama/Llama-3.2-3B-Instruct
# or
export LLAMA_STACK_MODEL=meta-llama/Llama-3.1-8B-Instruct
```

Test the connection:

```bash
API_KEY=none
LLAMA_STACK_ENDPOINT=http://localhost:8321

curl -sS $LLAMA_STACK_ENDPOINT/v1/inference/chat-completion \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY" \
  -d "{
     \"model_id\": \"$LLAMA_STACK_MODEL\",
     \"messages\": [{\"role\": \"user\", \"content\": \"What are the current departures from Arkadian puisto in Helsinki?\"}],
     \"temperature\": 0.0
   }" | jq -r '.completion_message | select(.role == "assistant") | .content'
```



