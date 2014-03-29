from django.dispatch import Signal


# sent just after a new connection is created and saved to the database.
# sender is the connection's relationship.
connection_created = Signal(providing_args=['connection'])


# sent just after a connection is deleted.
# sender is the connection's relationship.
connection_removed = Signal(providing_args=['connection'])
