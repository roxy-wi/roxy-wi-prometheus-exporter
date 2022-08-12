# Roxy-WI Prometheus exporter

Roxy-WI Prometheus exporter is on beta now. If you have a lack of metrics or faced 
with any problems, please [write to us](https://roxy-wi.org/contacts).

Roxy-WI Prometheus exporter exposes next metrics:

```# HELP python_gc_objects_collected_total Objects collected during gc
# TYPE python_gc_objects_collected_total counter
python_gc_objects_collected_total{generation="0"} 1180.0
python_gc_objects_collected_total{generation="1"} 265.0
python_gc_objects_collected_total{generation="2"} 0.0
# HELP python_gc_objects_uncollectable_total Uncollectable object found during GC
# TYPE python_gc_objects_uncollectable_total counter
python_gc_objects_uncollectable_total{generation="0"} 0.0
python_gc_objects_uncollectable_total{generation="1"} 0.0
python_gc_objects_uncollectable_total{generation="2"} 0.0
# HELP python_gc_collections_total Number of times this generation was collected
# TYPE python_gc_collections_total counter
python_gc_collections_total{generation="0"} 82.0
python_gc_collections_total{generation="1"} 7.0
python_gc_collections_total{generation="2"} 0.0
# HELP python_info Python platform information
# TYPE python_info gauge
python_info{implementation="CPython",major="3",minor="6",patchlevel="8",version="3.6.8"} 1.0
# HELP process_virtual_memory_bytes Virtual memory size in bytes.
# TYPE process_virtual_memory_bytes gauge
process_virtual_memory_bytes 3.64716032e+08
# HELP process_resident_memory_bytes Resident memory size in bytes.
# TYPE process_resident_memory_bytes gauge
process_resident_memory_bytes 2.4092672e+07
# HELP process_start_time_seconds Start time of the process since unix epoch in seconds.
# TYPE process_start_time_seconds gauge
process_start_time_seconds 1.66028387313e+09
# HELP process_cpu_seconds_total Total user and system CPU time spent in seconds.
# TYPE process_cpu_seconds_total counter
process_cpu_seconds_total 1.74
# HELP process_open_fds Number of open file descriptors.
# TYPE process_open_fds gauge
process_open_fds 7.0
# HELP process_max_fds Maximum number of open file descriptors.
# TYPE process_max_fds gauge
process_max_fds 1024.0
# HELP roxy_wi_services_total How many services
# TYPE roxy_wi_services_total gauge
roxy_wi_services_total{name="HAProxy",service="haproxy"} 2.0
roxy_wi_services_total{name="NGINX",service="nginx"} 3.0
roxy_wi_services_total{name="Keepalived",service="keepalived"} 3.0
roxy_wi_services_total{name="Apache",service="apache"} 1.0
# HELP roxy_wi_server_total How many servers
# TYPE roxy_wi_server_total gauge
roxy_wi_server_total 3.0
# HELP roxy_wi_enabled_server_total How many enabled servers
# TYPE roxy_wi_enabled_server_total gauge
roxy_wi_enabled_server_total 3.0
# HELP roxy_wi_virtual_server_total How many virtual servers
# TYPE roxy_wi_virtual_server_total gauge
roxy_wi_virtual_server_total 0.0
# HELP roxy_wi_user_total How many users
# TYPE roxy_wi_user_total gauge
roxy_wi_user_total 3.0
# HELP roxy_wi_user_by_role Users by roles
# TYPE roxy_wi_user_by_role gauge
roxy_wi_user_by_role{role="superAdmin"} 1.0
roxy_wi_user_by_role{role="admin"} 1.0
roxy_wi_user_by_role{role="user"} 1.0
roxy_wi_user_by_role{role="guest"} 0.0
# HELP roxy_wi_service_checker_enabled_total How many Checkers are enabled for service
# TYPE roxy_wi_service_checker_enabled_total gauge
roxy_wi_service_checker_enabled_total{name="HAProxy",service="haproxy"} 2.0
roxy_wi_service_checker_enabled_total{name="NGINX",service="nginx"} 3.0
roxy_wi_service_checker_enabled_total{name="Keepalived",service="keepalived"} 3.0
roxy_wi_service_checker_enabled_total{name="Apache",service="apache"} 1.0
# HELP roxy_wi_checker_enabled_total How many Checkers are enabled
# TYPE roxy_wi_checker_enabled_total gauge
roxy_wi_checker_enabled_total 9.0
# HELP roxy_wi_service_checker_alert Number of alerts per server
# TYPE roxy_wi_service_checker_alert gauge
roxy_wi_service_checker_alert{hostname="test-server",ip="10.0.0.205",level="info"} 10.0
roxy_wi_service_checker_alert{hostname="test-server",ip="10.0.0.205",level="warning"} 2.0
roxy_wi_service_checker_alert{hostname="test-server-2",ip="127.0.0.2",level="info"} 321.0
roxy_wi_service_checker_alert{hostname="test-server-2",ip="127.0.0.2",level="warning"} 64.0
roxy_wi_service_checker_alert{hostname="test-server-3",ip="127.0.0.4",level="info"} 266.0
roxy_wi_service_checker_alert{hostname="test-server-3",ip="127.0.0.4",level="warning"} 35.0
# HELP roxy_wi_service_checker_alert_total Total alerts
# TYPE roxy_wi_service_checker_alert_total gauge
roxy_wi_service_checker_alert_total{level="info"} 597.0
roxy_wi_service_checker_alert_total{level="warning"} 101.0
# HELP roxy_wi_service_auto_start_enabled_total How many Auto start are enabled for service
# TYPE roxy_wi_service_auto_start_enabled_total gauge
roxy_wi_service_auto_start_enabled_total{name="HAProxy",service="haproxy"} 2.0
roxy_wi_service_auto_start_enabled_total{name="NGINX",service="nginx"} 3.0
roxy_wi_service_auto_start_enabled_total{name="Keepalived",service="keepalived"} 3.0
roxy_wi_service_auto_start_enabled_total{name="Apache",service="apache"} 1.0
# HELP roxy_wi_auto_start_enabled_total How many Auto start are enabled
# TYPE roxy_wi_auto_start_enabled_total gauge
roxy_wi_auto_start_enabled_total 9.0
# HELP roxy_wi_service_metrics_enabled_total How many Metrics are enabled for service
# TYPE roxy_wi_service_metrics_enabled_total gauge
roxy_wi_service_metrics_enabled_total{name="HAProxy",service="haproxy"} 2.0
roxy_wi_service_metrics_enabled_total{name="NGINX",service="nginx"} 2.0
roxy_wi_service_metrics_enabled_total{name="Apache",service="apache"} 1.0
# HELP roxy_wi_metrics_enabled_total How many Metrics are enabled
# TYPE roxy_wi_metrics_enabled_total gauge
roxy_wi_metrics_enabled_total 5.0
```

# Installation

To install the exporter:

```angular2html
git clone https://github.com/hap-wi/roxy-wi-prometheus-exporter.git
cd roxy-wi-prometheus-exporter
pip3 install -r requirements.txt
chmod +x prometheus_exporter.py
mv prometheus_exporter.py /var/www/haproxy-wi/app/tools/
```

# Run:
```angular2html
cd /var/www/haproxy-wi/app
tools/prometheus_exporter.py &
```

# Dashboard
There is [dashboard for Grafana](https://grafana.com/grafana/dashboards/16713)

