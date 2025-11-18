# MCP Dubai RTA Bus Server Helm Chart

This Helm chart deploys the MCP Dubai RTA Bus Server on Kubernetes. The server provides access to Dubai public bus transportation data through the Dubai RTA real-time API.

## Features

- **Real-time Bus Information**: Get live bus arrival information for Dubai RTA bus stops
- **Route Information**: Access detailed bus route information and schedules
- **Stop Search**: Search for bus stops by name or coordinates
- **API Key Required**: Uses the Dubai RTA API with authentication

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
helm install my-dubai-transport mcp-servers/mcp-dubai-transport
```

Or install from local chart:
```bash
helm install my-dubai-transport ./mcp-dubai-transport
```

## Configuration

The following table lists the configurable parameters and their default values:

| Parameter | Description | Default |
|-----------|-------------|---------|
| `replicaCount` | Number of replicas | `1` |
| `image.repository` | Container image repository | `quay.io/bluesman/mcp-dubai-transport` |
| `image.tag` | Container image tag | `1.0.0` |
| `image.pullPolicy` | Image pull policy | `IfNotPresent` |
| `service.type` | Service type | `ClusterIP` |
| `service.port` | Service port | `80` |
| `service.targetPort` | Container port | `8000` |
| `transport.apiUrl` | Dubai RTA API URL | `https://www.rta.ae/links` |
| `transport.apiKey` | Dubai RTA API Key | `""` |
| `transport.cacheTtl` | Cache TTL in seconds | `300` |
| `transport.requestTimeout` | API request timeout in seconds | `30` |

## Examples

### Basic Installation
```bash
helm install dubai-transport ./mcp-dubai-transport
```

### Custom Configuration
```bash
helm install dubai-transport ./mcp-dubai-transport \
  --set replicaCount=2 \
  --set transport.cacheTtl=600 \
  --set transport.requestTimeout=45
```

### Using a Values File
Create a `custom-values.yaml` file:
```yaml
replicaCount: 2
transport:
  apiKey: "your-rta-api-key"
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
helm install dubai-transport ./mcp-dubai-transport -f custom-values.yaml
```

## MCP Tools Available

The server provides the following MCP tools:

1. **get_bus_arrivals**: Get real-time bus arrivals for a Dubai RTA bus stop
   - Parameters: `stop_code` (string) - RTA bus stop code

2. **search_bus_stops**: Search for Dubai RTA bus stops
   - Parameters: `query` (string) - Search query for bus stop name or location

3. **get_route_info**: Get information about a specific bus route
   - Parameters: `route_id` (string) - RTA bus route ID

## Data Features

The server provides rich information including:
- **Real-time bus arrivals** with countdown timers
- **Route information** with complete route details
- **Stop locations** with GPS coordinates
- **Service schedules** and frequency information
- **Bus network coverage** across Dubai

## Uninstallation

To uninstall the chart:
```bash
helm uninstall dubai-transport
```

## Support

For issues and support:
- GitHub: https://github.com/company/llama-stack-mcp-server
- Documentation: https://docs.company.com/mcp-dubai-transport