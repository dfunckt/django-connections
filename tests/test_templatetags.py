from django.contrib.auth.models import User
from django.template import Template, Context
from django.test import TestCase

from connections.models import Connection, _relationship_registry as registry
from connections.shortcuts import (define_relationship, get_relationship,
    create_connection)


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
    
    def test_get_connection_distance(self):
        tpl = """{%% spaceless %%}
            {%% load connections %%}
            {%% get_connection_distance %s foo bar as distance %%}
            {{ distance }}
        {%% endspaceless %%}"""
        
        create_connection(self.r, self.foo, self.bar)
        
        assert '1' == Template(tpl % "'user_follow'").render(Context({
            'foo': self.foo,
            'bar': self.bar,
        }))
        
        assert '1' == Template(tpl % "rel").render(Context({
            'rel': self.r,
            'foo': self.foo,
            'bar': self.bar,
        }))
    
    def test_connections_from_object(self):
        tpl = """{%% spaceless %%}
            {%% load connections %%}
            {%% connections_from_object %s foo as connections %%}
            {%% for c in connections %%}{{ c.to_object.username }}, {%% endfor %%}
        {%% endspaceless %%}"""
        
        create_connection(self.r, self.foo, self.bar)
        create_connection(self.r, self.foo, self.jaz)
        
        assert 'bar, jaz,' == Template(tpl % "'user_follow'").render(Context({
            'foo': self.foo,
        }))
        
        assert 'bar, jaz,' == Template(tpl % "rel").render(Context({
            'rel': self.r,
            'foo': self.foo,
        }))
    
    def test_connections_to_object(self):
        tpl = """{%% spaceless %%}
            {%% load connections %%}
            {%% connections_to_object %s foo as connections %%}
            {%% for c in connections %%}{{ c.from_object.username }}, {%% endfor %%}
        {%% endspaceless %%}"""
        
        create_connection(self.r, self.bar, self.foo)
        create_connection(self.r, self.jaz, self.foo)
        
        assert 'bar, jaz,' == Template(tpl % "'user_follow'").render(Context({
            'foo': self.foo,
        }))
        
        assert 'bar, jaz,' == Template(tpl % "rel").render(Context({
            'rel': self.r,
            'foo': self.foo,
        }))
    
    def test_connection_exists(self):
        tpl = """{%% spaceless %%}
            {%% load connections %%}
            {%% connection_exists %s foo bar as has_connection %%}
            {{ has_connection|yesno:'True,False' }}
        {%% endspaceless %%}"""
        
        create_connection(self.r, self.foo, self.bar)
        
        assert 'True' == Template(tpl % "'user_follow'").render(Context({
            'foo': self.foo,
            'bar': self.bar,
        }))
        
        assert 'True' == Template(tpl % "rel").render(Context({
            'rel': self.r,
            'foo': self.foo,
            'bar': self.bar,
        }))
