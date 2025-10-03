## Stockholm Transport MCP Server

MCP server for Stockholm public transportation data using Trafiklab Realtime API.

## Local Development and Testing

### Setup a venv

```bash
python3.11 -m venv venv
source venv/bin/activate
```

### Install dependencies

```bash
pip install fastmcp==2.2.2
```

### Run MCP Server

Note: runs on port 8000 by default

```bash
python stockholm_transport.py
```

### Test the server

```bash
python test_stockholm_transport.py
```

## Available Tools

The server provides the following tools:

- `get_departures`: Get real-time departures for Stockholm area (default area ID: 740098000)
- `get_arrivals`: Get real-time arrivals for Stockholm area
- `get_departures_and_arrivals`: Get both departures and arrivals in a single request

## API Information

- **API Base URL**: https://realtime-api.trafiklab.se/v1
- **API Key**: Your Trafiklab API Key for Real Time API
- **Default Area ID**: 740098000 (Stockholm)
- **Documentation**: https://www.trafiklab.se/api/our-apis/trafiklab-realtime-apis/openapi-specification/

## Llama Stack Integration

### Review Tools

First check to see which tools are already registered:

```bash
LLAMA_STACK_ENDPOINT=http://localhost:8321
curl -sS $LLAMA_STACK_ENDPOINT/v1/toolgroups -H "Content-Type: application/json" | jq
```

### Register the Stockholm Transport MCP server

If running Llama Stack in a container:

```bash
curl -X POST -H "Content-Type: application/json" --data '{ "provider_id" : "model-context-protocol", "toolgroup_id" : "mcp::stockholm-transport", "mcp_endpoint" : { "uri" : "http://host.docker.internal:8000/sse"}}' $LLAMA_STACK_ENDPOINT/v1/toolgroups
```

Else:

```bash
curl -X POST -H "Content-Type: application/json" --data '{ "provider_id" : "model-context-protocol", "toolgroup_id" : "mcp::stockholm-transport", "mcp_endpoint" : { "uri" : "http://localhost:8000/sse"}}' $LLAMA_STACK_ENDPOINT/v1/toolgroups
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
     \"messages\": [{\"role\": \"user\", \"content\": \"What are the current departures in Stockholm?\"}],
     \"temperature\": 0.0
   }" | jq -r '.completion_message | select(.role == "assistant") | .content'
```



