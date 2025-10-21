# MCP Helsinki Transport Server Helm Chart

This Helm chart deploys the MCP Helsinki Transport Server on Kubernetes. The server provides access to Helsinki public transportation data through the HSL Digitransit API.

## Features

- **Real-time Departures**: Get current departure information for Helsinki area
- **Real-time Arrivals**: Get current arrival information for Helsinki area
- **Combined Data**: Retrieve both departures and arrivals in a single request
- **HSL Integration**: Uses the HSL Digitransit GraphQL API

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
helm install my-helsinki-transport mcp-servers/mcp-helsinki-transport
```

Or install from local chart:
```bash
helm install my-helsinki-transport ./mcp-helsinki-transport
```

## Configuration

The following table lists the configurable parameters and their default values:

| Parameter | Description | Default |
|-----------|-------------|---------|
| `replicaCount` | Number of replicas | `1` |
| `image.repository` | Container image repository | `quay.io/bluesman/mcp-helsinki-transport` |
| `image.tag` | Container image tag | `1.0.0` |
| `image.pullPolicy` | Image pull policy | `IfNotPresent` |
| `service.type` | Service type | `ClusterIP` |
| `service.port` | Service port | `80` |
| `service.targetPort` | Container port | `8000` |
| `transport.digitransitApiKey` | Digitransit API key for HSL | `your_key` |
| `transport.defaultStopId` | Default stop ID (HSL:1080701 = Katajanokka) | `HSL:1080701` |

## Examples

### Basic Installation
```bash
helm install helsinki-transport ./mcp-helsinki-transport
```

### Custom Configuration
```bash
helm install helsinki-transport ./mcp-helsinki-transport \
  --set replicaCount=2 \
  --set transport.digitransitApiKey=YOUR_API_KEY \
  --set transport.defaultStopId=HSL:1173434
```

### Using a Values File
Create a `custom-values.yaml` file:
```yaml
replicaCount: 2
transport:
  digitransitApiKey: "YOUR_API_KEY"
  defaultStopId: "HSL:1080701"  # Katajanokka (near Scandic Grand Marina)
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
helm install helsinki-transport ./mcp-helsinki-transport -f custom-values.yaml
```

## MCP Tools Available

The server provides the following MCP tools:

1. **find_stop**: Find stops by name and get their IDs
   - Parameters: `name` (required), `limit` (optional, default: 10)
   - Example: Search for "Kamppi" to find all stops matching that name and their stop IDs

2. **get_departures**: Get real-time departures for a specific stop
   - Parameters: `stop_id` (optional, default: HSL:1080701), `limit` (optional, default: 10)

3. **get_timetable**: Get timetable for a stop within a specific time range
   - Parameters: `stop_id` (optional, default: HSL:1080701), `start_time` (optional, default: 0), `time_range` (optional, default: 3600)

4. **get_stop_info**: Get detailed information about a specific stop
   - Parameters: `stop_id` (required)

## Uninstallation

To uninstall the chart:
```bash
helm uninstall helsinki-transport
```

## API Information

- **API Documentation**: https://digitransit.fi/en/developers/apis/1-routing-api/
- **Base URL**: https://api.digitransit.fi/routing/v2/hsl/gtfs/v1
- **Default Stop ID**: HSL:1080701 (Katajanokka, near Scandic Grand Marina)
- **API Type**: GraphQL

## Support

For issues and support:
- GitHub: https://github.com/company/llama-stack-mcp-server
- Documentation: https://docs.company.com/mcp-helsinki-transport
- HSL API: https://digitransit.fi
