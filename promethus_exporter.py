#!/usr/bin/env python3
import os
import sys
from functools import lru_cache
import logging
import signal

import argparse
from prometheus_client.core import GaugeMetricFamily, REGISTRY
from prometheus_client import make_wsgi_app
from wsgiref.simple_server import make_server

sys.path.append(os.path.join(sys.path[0], os.path.dirname(os.getcwd())))
sys.path.append(os.path.join(sys.path[0], os.getcwd()))
import modules.db.sql as sql

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)


@lru_cache(1)
def get_services_from_db():
    services = sql.select_services()

    return services


@lru_cache(1)
def get_servers_from_db():
    servers = sql.select_servers(full=1)

    return servers


@lru_cache(1)
def get_users_from_db():
    users = sql.select_users()

    return users


def get_service_name() -> dict:
    """Make a dict with services Name and Slug"""
    services_name = {}
    services = get_services_from_db()

    for service in services:
        services_name[service.slug] = service.service
        services_name[service.service_id] = service.slug

    return services_name


class GracefulKiller:
    kill_now = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        logging.info('Roxy-WI Prometheus has been stopped')
        self.kill_now = True
        sys.exit()


class GeneralInfo(object):
    """Collect general info about Roxy-WI"""

    def __init__(self):
        pass

    @staticmethod
    def collect():
        virtual = 0
        enabled = 0

        servers = get_servers_from_db()
        users = get_users_from_db()
        services = get_services_from_db()
        service_total = GaugeMetricFamily("roxy_wi_services_total", "Total number of services", labels=['service', 'name'])
        enabled_server_total = GaugeMetricFamily("roxy_wi_enabled_server_total", "Total number of servers marked as \"Enabled\" in the Servers-Servers section")
        virtual_server_total = GaugeMetricFamily("roxy_wi_virtual_server_total", "Total number of virtual servers")
        user_total = GaugeMetricFamily("roxy_wi_user_total", "Total number of users")
        user_by_role = GaugeMetricFamily("roxy_wi_user_by_role", "Total number of users sorted by roles", labels=['role'])
        server_total = GaugeMetricFamily("roxy_wi_server_total", "Total number of servers")

        for server in servers:
            if server[4] == 1:
                virtual += 1
            if server[5] == 1:
                enabled += 1

        for service in services:
            service_count = sql.select_count_services(service.slug)
            service_total.add_metric([service.slug, service.service], service_count)

        user_superadmin = 0
        user_admin = 0
        user_user = 0
        user_guest = 0

        for user in users:
            if user.role == 'superAdmin':
                user_superadmin += 1
            if user.role == 'admin':
                user_admin += 1
            if user.role == 'user':
                user_user += 1
            if user.role == 'guest':
                user_guest += 1

        server_total.add_metric([''], len(servers))
        enabled_server_total.add_metric([''], enabled)
        virtual_server_total.add_metric([''], virtual)
        user_total.add_metric([''], len(users))
        user_by_role.add_metric(['superAdmin'], user_superadmin)
        user_by_role.add_metric(['admin'], user_admin)
        user_by_role.add_metric(['user'], user_user)
        user_by_role.add_metric(['guest'], user_guest)
        yield service_total
        yield server_total
        yield enabled_server_total
        yield virtual_server_total
        yield user_total
        yield user_by_role


class ServiceChecker(object):
    """Collect metrics about the Checker service"""

    def __init__(self):
        pass

    @staticmethod
    def collect():
        checker_haproxy = 0
        checker_nginx = 0
        checker_keepalived = 0
        checker_apache = 0

        service_checker_enabled_total = GaugeMetricFamily("roxy_wi_service_checker_enabled_total",
                                                          "Number of running Checker services for each HAProxy, NGINX, Keepalived, Apache service",
                                                          labels=['service', 'name'])
        checker_enabled_total = GaugeMetricFamily("roxy_wi_checker_enabled_total", "Total number of running Checker services")
        service_check_status = GaugeMetricFamily("roxy_wi_checker_service_status", "Statuses of Apache, NGINX, Keepalived, HAProxy services",
                                                 labels=['service', 'name', 'check_type', 'ip', 'hostname'])

        # Fetch raw status data from the cache
        servers = get_servers_from_db()
        services_name = get_service_name()
        services_check_status = sql.select_checker_services_status()

        # Update Prometheus metrics
        for server in servers:
            if server[8] == 1:
                checker_haproxy += 1
            if server[19] == 1:
                checker_nginx += 1
            if server[23] == 1:
                checker_keepalived += 1
            if server[25] == 1:
                checker_apache += 1

            for status in services_check_status:
                if str(status.server_id) == str(server[0]):
                    service_check_status.add_metric(
                        [services_name[status.service_id],
                         services_name[services_name[status.service_id]],
                         status.service_check,
                         server[2], server[1]],
                        status.status
                    )

        checker_total = checker_haproxy + checker_nginx + checker_keepalived + checker_apache

        service_checker_enabled_total.add_metric(['haproxy', services_name['haproxy']], checker_haproxy)
        service_checker_enabled_total.add_metric(['nginx', services_name['nginx']], checker_nginx)
        service_checker_enabled_total.add_metric(['keepalived', services_name['keepalived']], checker_keepalived)
        service_checker_enabled_total.add_metric(['apache', services_name['apache']], checker_apache)
        checker_enabled_total.add_metric([''], checker_total)

        yield service_checker_enabled_total
        yield checker_enabled_total
        yield service_check_status

        # Fetch alerts
        info_alerts = 0
        warning_alerts = 0
        alerts = sql.alerts_history('Checker', 1)
        alert_by_server = {}

        service_checker_alert = GaugeMetricFamily(
            "roxy_wi_service_checker_alert",
            "Number of alerts per server",
            labels=['hostname', 'ip', 'level']
        )
        service_checker_alert_total = GaugeMetricFamily(
            "roxy_wi_service_checker_alert_total",
            "Total alerts",
            labels=['level']
        )

        for server in servers:
            alert_by_server.setdefault(server[2])
            alert_by_server[server[2]] = {'hostname': server[1], 'info': 0, 'warning': 0}

        for alert in alerts:
            if alert[2] not in alert_by_server:
                continue
            if alert[1] == 'info':
                info_alerts += 1
                alert_by_server[alert[2]]['info'] += 1
            else:
                warning_alerts += 1
                alert_by_server[alert[2]]['warning'] += 1

        for server_ip, value in alert_by_server.items():
            service_checker_alert.add_metric([value['hostname'], server_ip, 'info'], value['info'])
            service_checker_alert.add_metric([value['hostname'], server_ip, 'warning'], value['warning'])

        service_checker_alert_total.add_metric(['info'], info_alerts)
        service_checker_alert_total.add_metric(['warning'], warning_alerts)

        yield service_checker_alert
        yield service_checker_alert_total


class AutoStartChecker(object):
    """Collect metrics about the Checker service"""

    def __init__(self):
        pass

    @staticmethod
    def collect():
        auto_start_haproxy = 0
        auto_start_nginx = 0
        auto_start_keepalived = 0
        auto_start_apache = 0

        service_auto_start_enabled_total = GaugeMetricFamily("roxy_wi_service_auto_start_enabled_total",
                                                             "Number of running Auto start services for each HAProxy, NGINX, Keepalived, Apache service",
                                                             labels=['service', 'name'])
        auto_start_enabled_total = GaugeMetricFamily("roxy_wi_auto_start_enabled_total",
                                                     "Number of running Metrics services for each HAProxy, NGINX, Apache service")

        # Fetch raw status data from the cache
        servers = get_servers_from_db()
        services_name = get_service_name()

        # Update Prometheus metrics
        for server in servers:
            if server[12] == 1:
                auto_start_haproxy += 1
            if server[17] == 1:
                auto_start_nginx += 1
            if server[22] == 1:
                auto_start_keepalived += 1
            if server[25] == 1:
                auto_start_apache += 1

        auto_start_total = auto_start_haproxy + auto_start_nginx + auto_start_keepalived + auto_start_apache
        service_auto_start_enabled_total.add_metric(['haproxy', services_name['haproxy']], auto_start_haproxy)
        service_auto_start_enabled_total.add_metric(['nginx', services_name['nginx']], auto_start_nginx)
        service_auto_start_enabled_total.add_metric(['keepalived', services_name['keepalived']], auto_start_keepalived)
        service_auto_start_enabled_total.add_metric(['apache', services_name['apache']], auto_start_apache)
        auto_start_enabled_total.add_metric([''], auto_start_total)

        yield service_auto_start_enabled_total
        yield auto_start_enabled_total


class MetricsChecker(object):
    """Collect metrics about the Metrics service"""

    def __init__(self):
        pass

    @staticmethod
    def collect():
        metrics_haproxy = 0
        metrics_nginx = 0
        metrics_apache = 0

        servers = get_servers_from_db()
        services_name = get_service_name()
        service_metrics_enabled_total = GaugeMetricFamily("roxy_wi_service_metrics_enabled_total",
                                                          "Number of running Metrics services for each HAProxy, NGINX, Apache service",
                                                          labels=['service', 'name'])
        metrics_enabled_total = GaugeMetricFamily("roxy_wi_metrics_enabled_total", "Total number of running Metrics services")

        for server in servers:
            if server[9] == 1:
                metrics_haproxy += 1
            if server[12] == 1:
                metrics_nginx += 1
            if server[27] == 1:
                metrics_apache += 1

        metrics_total = metrics_haproxy + metrics_nginx + metrics_apache

        service_metrics_enabled_total.add_metric(['haproxy', services_name['haproxy']], metrics_haproxy)
        service_metrics_enabled_total.add_metric(['nginx', services_name['nginx']], metrics_nginx)
        service_metrics_enabled_total.add_metric(['apache', services_name['apache']], metrics_apache)
        metrics_enabled_total.add_metric([''], metrics_total)

        yield service_metrics_enabled_total
        yield metrics_enabled_total


def expose_metrics(environ, start_fn):
    metrics_app = make_wsgi_app()
    if environ['PATH_INFO'] == '/metrics':
        return metrics_app(environ, start_fn)
    start_fn('200 OK', [])
    return [b'<a href="/metrics">/metrics</a>']


def main():
    """Main entry point"""

    parser = argparse.ArgumentParser(description='Roxy-WI Prometheus exporter.', prog='prometheus_exporter.py',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        '--address',
        help='Address on which to expose metrics and web interface.',
        nargs='?',
        type=str,
        default='0.0.0.0:9900'
    )

    args = parser.parse_args()
    try:
        bind_ip = args.address.split(':')[0]
        bind_port = int(args.address.split(':')[1])
    except Exception:
        print('error: wrong IP:PORT format')

    REGISTRY.register(GeneralInfo())
    REGISTRY.register(ServiceChecker())
    REGISTRY.register(AutoStartChecker())
    REGISTRY.register(MetricsChecker())
    httpd = make_server(bind_ip, bind_port, expose_metrics)
    httpd.serve_forever()


if __name__ == "__main__":
    logging.info('Roxy-WI Prometheus exporter has been started')
    killer = GracefulKiller()
    main()
