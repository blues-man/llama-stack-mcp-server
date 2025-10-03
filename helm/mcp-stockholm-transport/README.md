# MCP Stockholm Transport Server Helm Chart

This Helm chart deploys the MCP Stockholm Transport Server on Kubernetes. The server provides access to Stockholm public transportation data through the Trafiklab Realtime API.

## Features

- **Real-time Departures**: Get current departure information for Stockholm area
- **Real-time Arrivals**: Get current arrival information for Stockholm area
- **Combined Data**: Retrieve both departures and arrivals in a single request
- **Trafiklab Integration**: Uses the Trafiklab Realtime API with API key authentication

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
helm install my-stockholm-transport mcp-servers/mcp-stockholm-transport
```

Or install from local chart:
```bash
helm install my-stockholm-transport ./mcp-stockholm-transport
```

## Configuration

The following table lists the configurable parameters and their default values:

| Parameter | Description | Default |
|-----------|-------------|---------|
| `replicaCount` | Number of replicas | `1` |
| `image.repository` | Container image repository | `quay.io/bluesman/mcp-stockholm-transport` |
| `image.tag` | Container image tag | `1.0.0` |
| `image.pullPolicy` | Image pull policy | `IfNotPresent` |
| `service.type` | Service type | `ClusterIP` |
| `service.port` | Service port | `80` |
| `service.targetPort` | Container port | `8000` |
| `transport.apiUrl` | Stockholm transport API URL | `https://realtime-api.trafiklab.se/v1` |
| `transport.apiKey` | Trafiklab API key | `your_key` |
| `transport.areaId` | Stockholm area ID | `740098000` |
| `transport.cacheTtl` | Cache TTL in seconds | `300` |
| `transport.defaultLimit` | Default search result limit | `10` |
| `transport.requestTimeout` | API request timeout in seconds | `30` |

## Examples

### Basic Installation
```bash
helm install stockholm-transport ./mcp-stockholm-transport
```

### Custom Configuration
```bash
helm install stockholm-transport ./mcp-stockholm-transport \
  --set replicaCount=2 \
  --set transport.defaultLimit=20 \
  --set transport.cacheTtl=600
```

### Using a Values File
Create a `custom-values.yaml` file:
```yaml
replicaCount: 2
transport:
  defaultLimit: 20
  cacheTtl: 600
  areaId: "740098000"  # Stockholm area
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
helm install stockholm-transport ./mcp-stockholm-transport -f custom-values.yaml
```

## MCP Tools Available

The server provides the following MCP tools:

1. **get_departures**: Get real-time departures for Stockholm area
   - Parameters: `area_id` (optional, default: 740098000), `limit` (optional, default: 10)

2. **get_arrivals**: Get real-time arrivals for Stockholm area
   - Parameters: `area_id` (optional, default: 740098000), `limit` (optional, default: 10)

3. **get_departures_and_arrivals**: Get both departures and arrivals in a single request
   - Parameters: `area_id` (optional, default: 740098000), `limit` (optional, default: 10)

## Uninstallation

To uninstall the chart:
```bash
helm uninstall stockholm-transport
```

## API Information

- **API Documentation**: https://www.trafiklab.se/api/our-apis/trafiklab-realtime-apis/openapi-specification/
- **Base URL**: https://realtime-api.trafiklab.se/v1
- **Default Area ID**: 740098000 (Stockholm)

## Support

For issues and support:
- GitHub: https://github.com/company/llama-stack-mcp-server
- Documentation: https://docs.company.com/mcp-stockholm-transport
- Trafiklab API: https://www.trafiklab.se
