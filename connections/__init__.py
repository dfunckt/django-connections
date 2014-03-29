from .shortcuts import (
    define_relationship,
    get_relationship,
    get_connection,
    create_connection,
    connection_exists,
    connections_from_object,
    connections_to_object,
    connected_objects,
    connected_to_objects,
)

VERSION = (0, 2, 0, 'final', 1)

default_app_config = 'connections.apps.ConnectionsConfig'
