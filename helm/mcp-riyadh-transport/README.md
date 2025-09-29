# MCP Riyadh Transport Server Helm Chart

This Helm chart deploys the MCP Riyadh Transport Server on Kubernetes. The server provides access to Riyadh public transportation data through the RCRC (Riyadh Public Transport Company) open data API.

## Features

- **Bus Route Search**: Search for bus routes by various criteria (route number, origin, destination)
- **Route Details**: Get detailed information about specific bus routes including GPS waypoints
- **Area-based Search**: Find all bus routes serving a specific area or neighborhood
- **Route Listing**: Browse all available bus routes in Riyadh
- **Multilingual Support**: Display route information in both English and Arabic
- **No API Key Required**: Uses the free RCRC open data API

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
helm install my-riyadh-transport mcp-servers/mcp-riyadh-transport
```

Or install from local chart:
```bash
helm install my-riyadh-transport ./mcp-riyadh-transport
```

## Configuration

The following table lists the configurable parameters and their default values:

| Parameter | Description | Default |
|-----------|-------------|---------|
| `replicaCount` | Number of replicas | `1` |
| `image.repository` | Container image repository | `quay.io/bluesman/mcp-riyadh-transport` |
| `image.tag` | Container image tag | `1.0.0` |
| `image.pullPolicy` | Image pull policy | `IfNotPresent` |
| `service.type` | Service type | `ClusterIP` |
| `service.port` | Service port | `80` |
| `service.targetPort` | Container port | `8000` |
| `transport.apiUrl` | RCRC API URL | `https://opendata.rcrc.gov.sa/api/explore/v2.1/catalog/datasets` |
| `transport.datasetName` | Dataset name for bus routes | `bus-roads-by-direction-in-riyadh-2024` |
| `transport.cacheTtl` | Cache TTL in seconds | `300` |
| `transport.defaultRoutes` | Default route codes for common routes | `["L19-1", "L11-1", "L13-1"]` |
| `transport.requestTimeout` | API request timeout in seconds | `30` |

## Examples

### Basic Installation
```bash
helm install riyadh-transport ./mcp-riyadh-transport
```

### Custom Configuration
```bash
helm install riyadh-transport ./mcp-riyadh-transport \
  --set replicaCount=2 \
  --set transport.cacheTtl=600 \
  --set transport.requestTimeout=45
```

### Using a Values File
Create a `custom-values.yaml` file:
```yaml
replicaCount: 2
transport:
  cacheTtl: 600
  defaultRoutes:
    - "L19-1"  # Transportation Center → King Saud University
    - "L11-1"  # West Al-Uraija → Ar Rabi
    - "L13-1"  # As-Sulaimanyah → National Guard Hospital
    - "L46-1"  # Riyadh Exhibition Center → Al Arid
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
helm install riyadh-transport ./mcp-riyadh-transport -f custom-values.yaml
```

## MCP Tools Available

The server provides the following MCP tools:

1. **search_bus_routes**: Search for bus routes by various criteria
   - Parameters: `query`, `route_number`, `origin`, `destination`, `limit`

2. **get_route_details**: Get detailed information about a specific bus route
   - Parameters: `route_code` (string) - Bus route code (e.g., "L19-1")

3. **list_all_routes**: List all available bus routes in Riyadh
   - Parameters: `limit` (int, optional) - Maximum number of routes to return

4. **search_routes_by_area**: Search for bus routes serving a specific area
   - Parameters: `area_name` (string), `limit` (int, optional)

## Sample Routes

| Route Code | Route Number | Origin | Destination |
|------------|--------------|---------|-------------|
| L19-1 | 7 | Transportation Center | King Saud University |
| L11-1 | 730 | West Al-Uraija | Ar Rabi |
| L13-1 | 250 | As-Sulaimanyah | National Guard Hospital |
| L46-1 | 231 | Riyadh Exhibition Center | Al Arid |

## Data Features

The server provides rich information including:
- **Route codes and numbers** for easy identification
- **Multilingual support** (English and Arabic names)
- **Geographic information** including GPS coordinates and route waypoints
- **Direction information** for different route directions
- **Complete route mapping** with start and end points
- **Route comments** in both languages

## Environment Variables

The chart sets the following environment variables in the container:

| Variable | Description | Value Source |
|----------|-------------|--------------|
| `MCP_SERVER_PORT` | Server port | `env.MCP_SERVER_PORT` |
| `MCP_SERVER_HOST` | Server host | `env.MCP_SERVER_HOST` |
| `RIYADH_API_BASE` | RCRC API base URL | `transport.apiUrl` |
| `DATASET_NAME` | Dataset name | `transport.datasetName` |
| `TRANSPORT_CACHE_TTL` | Cache TTL | `transport.cacheTtl` |
| `TRANSPORT_REQUEST_TIMEOUT` | Request timeout | `transport.requestTimeout` |
| `DEFAULT_ROUTES` | Default route codes | `transport.defaultRoutes` (joined) |

## Uninstallation

To uninstall the chart:
```bash
helm uninstall riyadh-transport
```

## Support

For issues and support:
- GitHub: https://github.com/company/llama-stack-mcp-server
- Documentation: https://docs.company.com/mcp-riyadh-transport

## API Reference

This server uses the RCRC (Riyadh Public Transport Company) open data API:
- Base URL: https://opendata.rcrc.gov.sa/api/explore/v2.1/catalog/datasets/
- Dataset: bus-roads-by-direction-in-riyadh-2024
- Data format: JSON with detailed route and geographic information
- No authentication required