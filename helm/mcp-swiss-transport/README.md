# MCP Swiss Transport Server Helm Chart

This Helm chart deploys the MCP Swiss Transport Server on Kubernetes. The server provides access to Swiss public transportation data through the transport.opendata.ch API.

## Features

- **Connection Search**: Find public transportation routes between any Swiss locations
- **Location Search**: Search for stations and stops by name
- **Station Board**: Get real-time departure information for any station
- **No API Key Required**: Uses the free transport.opendata.ch API

## Prerequisites

- Kubernetes 1.19+
- Helm 3.2.0+

## Installation

1. Add the repository (if available):
```bash
helm repo add mcp-servers https://your-repo-url
helm repo update
```

2. Install the chart:
```bash
helm install my-swiss-transport mcp-servers/mcp-swiss-transport
```

Or install from local chart:
```bash
helm install my-swiss-transport ./mcp-public-swiss
```

## Configuration

The following table lists the configurable parameters and their default values:

| Parameter | Description | Default |
|-----------|-------------|---------|
| `replicaCount` | Number of replicas | `1` |
| `image.repository` | Container image repository | `quay.io/rh-aiservices-bu/mcp-swiss-transport` |
| `image.tag` | Container image tag | `0.1.0-amd64` |
| `image.pullPolicy` | Image pull policy | `IfNotPresent` |
| `service.type` | Service type | `ClusterIP` |
| `service.port` | Service port | `80` |
| `service.targetPort` | Container port | `3001` |
| `transport.apiUrl` | Swiss transport API URL | `http://transport.opendata.ch/v1` |
| `transport.cacheTtl` | Cache TTL in seconds | `300` |
| `transport.defaultLimit` | Default search result limit | `4` |
| `transport.requestTimeout` | API request timeout in seconds | `30` |

## Examples

### Basic Installation
```bash
helm install swiss-transport ./mcp-public-swiss
```

### Custom Configuration
```bash
helm install swiss-transport ./mcp-public-swiss \
  --set replicaCount=2 \
  --set transport.defaultLimit=10 \
  --set transport.cacheTtl=600
```

### Using a Values File
Create a `custom-values.yaml` file:
```yaml
replicaCount: 2
transport:
  defaultLimit: 10
  cacheTtl: 600
resources:
  limits:
    cpu: 1000m
    memory: 1Gi
  requests:
    cpu: 500m
    memory: 512Mi
```

Install with custom values:
```bash
helm install swiss-transport ./mcp-public-swiss -f custom-values.yaml
```

## MCP Tools Available

The server provides the following MCP tools:

1. **search_connections**: Find public transportation connections between locations
   - Parameters: `from_location`, `to_location`, `date` (optional), `time` (optional), `limit` (optional)

2. **search_locations**: Search for stations and locations by name
   - Parameters: `query`, `limit` (optional)

3. **get_stationboard**: Get departure board for a specific station
   - Parameters: `station`, `limit` (optional), `transportation_types` (optional)

## Uninstallation

To uninstall the chart:
```bash
helm uninstall swiss-transport
```

## Support

For issues and support:
- GitHub: https://github.com/company/llama-stack-mcp-server
- Documentation: https://docs.company.com/mcp-swiss-transport