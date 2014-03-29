from django.apps import AppConfig


class ConnectionsConfig(AppConfig):
    name = 'connections'


class AutodiscoverConnectionsConfig(ConnectionsConfig):
    def ready(self):
        from django.utils.module_loading import autodiscover_modules
        autodiscover_modules('relationships')
