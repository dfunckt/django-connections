from nose.tools import assert_raises, with_setup

try:
    from nose.tools import assert_raises_regex
except ImportError:
    from nose.tools import assert_raises_regexp as assert_raises_regex

from django.contrib.auth.models import User

from connections.models import (NAME_MAX_LENGTH, get_model,
    Relationship, Connection, _relationship_registry as registry)
from connections.shortcuts import define_relationship, get_relationship


def reset_registry(d):
    def fn():
        for k in list(d.keys()):
            d.pop(k)
    return fn


def test_get_model():
    assert Connection is get_model(Connection)
    assert Connection is get_model('connections.Connection')
    assert_raises_regex(ValueError, "^<(class|type) 'object'>$", get_model, object)
    assert_raises_regex(ValueError, '^invalidmodelname$', get_model, 'invalidmodelname')
    assert_raises_regex(ValueError, '^invalid\.Model$', get_model, 'invalid.Model')


@with_setup(reset_registry(registry), reset_registry(registry))
def test_define_relationship():
    r1 = define_relationship('rel1', 'auth.User', 'auth.User')
    assert 'rel1' in registry
    assert r1 in registry.values()
    assert isinstance(r1, Relationship)
    assert r1.name == 'rel1'
    assert r1.from_content_type.model_class() is User
    assert r1.to_content_type.model_class() is User
    assert str(r1) == 'rel1 (user -> user)'
    
    r2 = define_relationship('rel2', User, User)
    assert 'rel2' in registry
    assert r2 in registry.values()
    assert isinstance(r2, Relationship)
    assert r2.name == 'rel2'
    assert r2.from_content_type.model_class() is User
    assert r2.to_content_type.model_class() is User
    assert str(r2) == 'rel2 (user -> user)'


@with_setup(reset_registry(registry), reset_registry(registry))
def test_define_relationship_raises_for_duplicate():
    define_relationship('r1', User, User)
    assert_raises_regex(KeyError, "^'r1'$", define_relationship, 'r1', User, User)


@with_setup(reset_registry(registry), reset_registry(registry))
def test_relationship_name_max_length():
    assert_raises(AssertionError, define_relationship, 'x' * (NAME_MAX_LENGTH + 1), User, User)
    define_relationship('x' * NAME_MAX_LENGTH, User, User)


@with_setup(reset_registry(registry), reset_registry(registry))
def test_get_relationship():
    r = define_relationship('rel', User, User)
    assert r is get_relationship('rel')
    assert r is get_relationship(r)
    assert_raises(Relationship.DoesNotExist, get_relationship, 'invalid')
