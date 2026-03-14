# Grafana Dashboards

The monitoring stack includes several useful Grafana dashboards.

## Kubernetes Cluster Monitoring
Dashboard ID: 3119

Shows:
- CPU usage
- Memory usage
- Cluster health

## Node Exporter
Dashboard ID: 1860

Shows:
- Node CPU
- Disk usage
- Network metrics

## Kubernetes Pods Monitoring
Dashboard ID: 6417

Shows:
- Pod CPU usage
- Pod memory usage
- Pod restarts

## Logs check
Grafana -> Explore -> Loki

Query:
{job="varlogs"}