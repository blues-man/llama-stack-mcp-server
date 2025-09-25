# MCP Vienna Transport Server Helm Chart

This Helm chart deploys the MCP Vienna Transport Server on Kubernetes. The server provides access to Vienna public transportation data through the Wiener Linien real-time API.

## Features

- **Real-time Station Monitor**: Get live departure information for Vienna public transport stations
- **Multiple Station Monitoring**: Monitor multiple stations simultaneously using RBL numbers
- **Station Search Guidance**: Help finding RBL numbers for Vienna stations
- **No API Key Required**: Uses the free Wiener Linien open data API

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
helm install my-vienna-transport mcp-servers/mcp-vienna-transport
```

Or install from local chart:
```bash
helm install my-vienna-transport ./mcp-vienna-transport
```

## Configuration

The following table lists the configurable parameters and their default values:

| Parameter | Description | Default |
|-----------|-------------|---------|
| `replicaCount` | Number of replicas | `1` |
| `image.repository` | Container image repository | `quay.io/bluesman/mcp-vienna-transport` |
| `image.tag` | Container image tag | `1.0.0` |
| `image.pullPolicy` | Image pull policy | `IfNotPresent` |
| `service.type` | Service type | `ClusterIP` |
| `service.port` | Service port | `80` |
| `service.targetPort` | Container port | `8000` |
| `transport.apiUrl` | Wiener Linien API URL | `https://www.wienerlinien.at/ogd_realtime` |
| `transport.cacheTtl` | Cache TTL in seconds | `300` |
| `transport.defaultStations` | Default RBL numbers for common stations | `["4127", "4201", "4205"]` |
| `transport.requestTimeout` | API request timeout in seconds | `30` |

## Examples

### Basic Installation
```bash
helm install vienna-transport ./mcp-vienna-transport
```

### Custom Configuration
```bash
helm install vienna-transport ./mcp-vienna-transport \
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
  defaultStations:
    - "4127"  # Kagran U1
    - "4201"  # Stephansplatz U1
    - "4205"  # Karlsplatz U1
    - "4301"  # Westbahnhof U3
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
helm install vienna-transport ./mcp-vienna-transport -f custom-values.yaml
```

## MCP Tools Available

The server provides the following MCP tools:

1. **get_station_monitor**: Get real-time departures for a Vienna station using RBL number
   - Parameters: `rbl` (string) - RBL number for the station

2. **get_multiple_stations_monitor**: Get real-time departures for multiple stations
   - Parameters: `rbl_list` (string) - Comma-separated list of RBL numbers

3. **search_vienna_stations**: Search for Vienna stations and get guidance on RBL numbers
   - Parameters: `name` (string) - Station name to search for

## Common RBL Numbers

| Station | RBL Number | Line |
|---------|------------|------|
| Kagran | 4127 | U1 |
| Stephansplatz | 4201 | U1 |
| Karlsplatz | 4205 | U1 |
| Schwedenplatz | 4202 | U1 |
| Westbahnhof | 4301 | U3 |
| Schottentor | 4021 | U2 |

## Data Features

The server provides rich information including:
- **Real-time departures** with countdown timers
- **Platform information** and directions
- **Accessibility features** (barrier-free access, folding ramps)
- **Service disruptions** and traffic jam indicators
- **Multiple transport types** (U-Bahn, Straßenbahn, Bus)
- **Live vs. scheduled times** with delay information

## Uninstallation

To uninstall the chart:
```bash
helm uninstall vienna-transport
```

## Support

For issues and support:
- GitHub: https://github.com/company/llama-stack-mcp-server
- Documentation: https://docs.company.com/mcp-vienna-transport