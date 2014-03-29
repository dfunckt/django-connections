import re

from django.contrib.auth.models import User, Group
from django.test import TestCase

from connections.models import Connection, _relationship_registry as registry
from connections.shortcuts import (define_relationship, get_relationship,
    create_connection, get_connection, connection_exists,
    connections_from_object, connections_to_object,
    connected_objects, connected_to_objects)


def reset_registry(d):
    for k in list(d.keys()):
        d.pop(k)


def reset_relationship(r):
    Connection.objects.filter(relationship_name=get_relationship(r).name).delete()


class ConnectionTests(TestCase):
    def setUp(self):
        reset_registry(registry)
        self.r = define_relationship('user_follow', User, User)
        self.foo = User.objects.create_user(username='foo')
        self.bar = User.objects.create_user(username='bar')
        self.jaz = User.objects.create_user(username='jaz')
        reset_relationship('user_follow')
    
    def tearDown(self):
        reset_relationship('user_follow')
        reset_registry(registry)
        self.foo.delete()
        self.bar.delete()
        self.jaz.delete()
    
    def test_validate_ctypes(self):
        group = Group.objects.create(name='testgroup')
        try:
            self.r._validate_ctypes(self.foo, self.bar)
            self.assertRaises(AssertionError, self.r._validate_ctypes, group, self.bar)
            self.assertRaises(AssertionError, self.r._validate_ctypes, self.bar, group)
        finally:
            group.delete()
    
    def test_create_connection(self):
        c = create_connection(self.r, self.foo, self.bar)
        assert c.relationship_name == self.r.name
        assert c.relationship is self.r
        assert c.from_object == self.foo
        assert c.to_object == self.bar
        assert re.match(r'user_follow \(user:\d+ --> user:\d+\)', str(c))
    
    def test_get_connection(self):
        c = create_connection(self.r, self.foo, self.bar)
        assert get_connection(self.r, self.foo, self.bar) == c
        assert get_connection(self.r, self.foo, self.jaz) is None
    
    def test_connection_exists(self):
        assert not connection_exists(self.r, self.foo, self.bar)
        create_connection(self.r, self.foo, self.bar)
        assert connection_exists(self.r, self.foo, self.bar)
    
    def test_connections_from_object(self):
        c1 = create_connection(self.r, self.foo, self.bar)
        c2 = create_connection(self.r, self.foo, self.jaz)
        assert set(connections_from_object(self.r, self.foo)) == set([c1, c2])
    
    def test_connections_to_object(self):
        c1 = create_connection(self.r, self.bar, self.foo)
        c2 = create_connection(self.r, self.jaz, self.foo)
        assert set(connections_to_object(self.r, self.foo)) == set([c1, c2])
    
    def test_connected_objects(self):
        create_connection(self.r, self.foo, self.bar)
        create_connection(self.r, self.foo, self.jaz)
        assert set(connected_objects(self.r, self.foo)) == set([self.bar, self.jaz])
    
    def test_connected_to_objects(self):
        create_connection(self.r, self.bar, self.foo)
        create_connection(self.r, self.jaz, self.foo)
        assert set(connected_to_objects(self.r, self.foo)) == set([self.bar, self.jaz])
    
    def test_connected_object_ids(self):
        create_connection(self.r, self.foo, self.bar)
        create_connection(self.r, self.foo, self.jaz)
        assert set(self.r.connected_object_ids(self.foo)) == set([self.bar.pk, self.jaz.pk])
    
    def test_connected_to_object_ids(self):
        create_connection(self.r, self.bar, self.foo)
        create_connection(self.r, self.jaz, self.foo)
        assert set(self.r.connected_to_object_ids(self.foo)) == set([self.bar.pk, self.jaz.pk])
    
    def test_distance_between(self):
        create_connection(self.r, self.foo, self.foo)
        create_connection(self.r, self.foo, self.bar)
        create_connection(self.r, self.bar, self.jaz)
        assert self.r.distance_between(self.foo, self.foo) == 0
        assert self.r.distance_between(self.foo, self.bar) == 1
        assert self.r.distance_between(self.foo, self.jaz) == 2
        assert self.r.distance_between(self.bar, self.jaz) == 1
        assert self.r.distance_between(self.bar, self.foo) is None
        assert self.r.distance_between(self.jaz, self.foo) is None
        assert self.r.distance_between(self.jaz, self.bar) is None
