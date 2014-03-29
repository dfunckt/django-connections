from nose.tools import with_setup

from django.contrib.auth.models import User

from connections.models import _relationship_registry as registry
from connections.shortcuts import define_relationship, create_connection
from connections.signals import connection_created, connection_removed


def reset_registry(d):
    def fn():
        for k in list(d.keys()):
            d.pop(k)
    return fn


@with_setup(reset_registry(registry), reset_registry(registry))
def test_connection_created():
    foo = User.objects.create_user(username='foo')
    bar = User.objects.create_user(username='bar')
    r = define_relationship('rel', User, User)
    
    def handler(signal, sender, connection, **kwargs):
        assert sender is r
        assert connection.relationship is r
        assert connection.from_object == foo
        assert connection.to_object == bar
        assert kwargs == {}
    
    c = None
    try:
        connection_created.connect(handler, sender=r)
        c = create_connection(r, foo, bar)
    finally:
        connection_created.disconnect(handler)
        c and c.delete()
        foo.delete()
        bar.delete()


@with_setup(reset_registry(registry), reset_registry(registry))
def test_connection_removed():
    foo = User.objects.create_user(username='foo')
    bar = User.objects.create_user(username='bar')
    r = define_relationship('rel', User, User)
    
    def handler(signal, sender, connection, **kwargs):
        assert sender is r
        assert connection.relationship is r
        assert connection.from_object == foo
        assert connection.to_object == bar
        assert kwargs == {}
    
    try:
        connection_removed.connect(handler, sender=r)
        c = create_connection(r, foo, bar)
        c.delete()
    finally:
        connection_removed.disconnect(handler)
        foo.delete()
        bar.delete()
