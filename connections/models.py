from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.utils import timezone

try:
    from django.apps import apps as loading
except ImportError:  # pragma: no cover
    # Django < 1.7
    from django.db.models import loading

from .signals import connection_created, connection_removed


NAME_MAX_LENGTH = 50


def get_model(model):
    """
    Given a model name as ``app_label.ModelName``, returns the Django model.
    """
    try:
        if isinstance(model, str):
            app_label, model_name = model.split('.', 1)
            m = loading.get_model(app_label, model_name)
            if not m:  # pragma: no cover
                raise LookupError()  # Django < 1.7 just returns None
            return m
        elif issubclass(model, models.Model):
            return model
    except (LookupError, ValueError):
        pass
    raise ValueError(model)


_relationship_registry = {}


def define_relationship(name, from_model, to_model):
    if name in _relationship_registry:
        raise KeyError(name)
    
    _from_ctype = from_model
    _to_ctype = to_model
    
    if isinstance(_from_ctype, str):
        _from_ctype = get_model(_from_ctype)
    if isinstance(_to_ctype, str):
        _to_ctype = get_model(_to_ctype)
    
    if not isinstance(_from_ctype, ContentType):
        _from_ctype = ContentType.objects.get_for_model(_from_ctype)
    if not isinstance(_to_ctype, ContentType):
        _to_ctype = ContentType.objects.get_for_model(_to_ctype)
    
    relationship = Relationship(name=name,
                                from_content_type=_from_ctype,
                                to_content_type=_to_ctype)
    
    _relationship_registry[name] = relationship
    return relationship


def get_relationship(name):
    if isinstance(name, Relationship):
        return name
    if name not in _relationship_registry:
        raise Relationship.DoesNotExist(name)
    return _relationship_registry[name]


class RelationshipDoesNotExist(ObjectDoesNotExist):
    """
    Exception thrown when a relationship is not found in the registry.
    """


class Relationship(object):
    """
    Represents a predefined type of connection between two nodes in a
    (directed) graph. You may imagine relationships as the *"flavour"*
    of an edge in the graph.
    """
    DoesNotExist = RelationshipDoesNotExist
    
    def __init__(self, name, from_content_type, to_content_type):
        assert len(name) <= NAME_MAX_LENGTH
        assert isinstance(from_content_type, ContentType)
        assert isinstance(to_content_type, ContentType)
        self.name = name
        self.from_content_type = from_content_type
        self.to_content_type = to_content_type
    
    def __str__(self):
        return '%s (%s -> %s)' % (self.name, self.from_content_type,
                                  self.to_content_type)
    
    def _validate_ctypes(self, from_obj, to_obj):
        """
        Asserts that the content types for the given object are valid for this
        relationship. If validation fails, ``AssertionError`` will be raised.
        """
        if from_obj:
            from_ctype = ContentType.objects.get_for_model(from_obj)
            assert from_ctype.natural_key() == self.from_content_type.natural_key(), (
                'Relationship "%s" does not support connections '
                'from "%s" types' % (self.name, from_ctype))
        if to_obj:
            to_ctype = ContentType.objects.get_for_model(to_obj)
            assert to_ctype.natural_key() == self.to_content_type.natural_key(), (
                'Relationship "%s" does not support connections '
                'to "%s" types' % (self.name, to_ctype))
    
    @property
    def connections(self):
        """
        Returns a query set matching all connections of this relationship.
        """
        return Connection.objects.filter(relationship_name=self.name)
    
    def create_connection(self, from_obj, to_obj):
        """
        Creates and returns a connection between the given objects. If a
        connection already exists, that connection will be returned instead.
        """
        self._validate_ctypes(from_obj, to_obj)
        return Connection.objects.get_or_create(relationship_name=self.name,
                                                from_pk=from_obj.pk, to_pk=to_obj.pk)[0]
    
    def get_connection(self, from_obj, to_obj):
        """
        Returns a ``Connection`` instance for the given objects or ``None`` if
        there's no connection.
        """
        self._validate_ctypes(from_obj, to_obj)
        try:
            return self.connections.get(from_pk=from_obj.pk, to_pk=to_obj.pk)
        except Connection.DoesNotExist:
            return None
    
    def connection_exists(self, from_obj, to_obj):
        """
        Returns ``True`` if a connection between the given objects exists,
        else ``False``.
        """
        self._validate_ctypes(from_obj, to_obj)
        return self.connections.filter(from_pk=from_obj.pk, to_pk=to_obj.pk).exists()
    
    def connections_from_object(self, from_obj):
        """
        Returns a ``Connection`` query set matching all connections with
        the given object as a source.
        """
        self._validate_ctypes(from_obj, None)
        return self.connections.filter(from_pk=from_obj.pk)
    
    def connections_to_object(self, to_obj):
        """
        Returns a ``Connection`` query set matching all connections with
        the given object as a destination.
        """
        self._validate_ctypes(None, to_obj)
        return self.connections.filter(to_pk=to_obj.pk)
    
    def connected_objects(self, from_obj):
        """
        Returns a query set matching all connected objects with the given
        object as a source.
        """
        return self.to_content_type.get_all_objects_for_this_type(pk__in=self.connected_object_ids(from_obj))
    
    def connected_object_ids(self, from_obj):
        """
        Returns an iterable of the IDs of all objects connected with the given
        object as a source (ie. the Connection.to_pk values).
        """
        return self.connections_from_object(from_obj).values_list('to_pk', flat=True)
    
    def connected_to_objects(self, to_obj):
        """
        Returns a query set matching all connected objects with the given
        object as a destination.
        """
        return self.from_content_type.get_all_objects_for_this_type(pk__in=self.connected_to_object_ids(to_obj))
    
    def connected_to_object_ids(self, to_obj):
        """
        Returns an iterable of the IDs of all objects connected with the given
        object as a destination (ie. the Connection.from_pk values).
        """
        return self.connections_to_object(to_obj).values_list('from_pk', flat=True)
    
    def distance_between(self, from_obj, to_obj, limit=2):
        """
        Calculates the distance between two objects. Distance 0 means
        ``from_obj`` and ``to_obj`` are the same objects, 1 means ``from_obj``
        has a direct connection to ``to_obj``, 2 means that one or more of
        ``from_obj``'s connected objects are directly connected to ``to_obj``,
        etc.
        
        ``limit`` limits the depth of connections traversal.
        
        Returns ``None`` if the two objects are not connected within ``limit``
        distance.
        """
        self._validate_ctypes(from_obj, to_obj)
        
        if from_obj == to_obj:
            return 0
        
        d = 1
        pk = to_obj.pk
        qs = self.connections
        pks = qs.filter(from_pk=from_obj.pk).values_list('to_pk', flat=True)
        while limit > 0:
            if pk in pks:
                return d
            else:
                pks = qs.filter(from_pk__in=pks).values_list('pk', flat=True)
                d += 1
                limit -= 1
        
        return None


class Connection(models.Model):
    """
    Represents a connection between two nodes in a graph. Connections must
    be treated as non-symmetrical (unidirectional), i.e. creating a connection
    from one node to another should not imply the reverse.
    
    You may imagine connections as the *edges* in a graph.
    """
    relationship_name = models.CharField(max_length=NAME_MAX_LENGTH)
    from_pk = models.IntegerField()
    to_pk = models.IntegerField()
    weight = models.FloatField(default=1.0, blank=True)
    date = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ('relationship_name', 'from_pk', 'to_pk')
    
    def __str__(self):
        rel = self.relationship
        return '%s (%s:%s --> %s:%s)' % (rel.name,
                                         rel.from_content_type, self.from_pk,
                                         rel.to_content_type, self.to_pk)
    
    @property
    def relationship(self):
        return get_relationship(self.relationship_name)
    
    @property
    def from_object(self):
        if not hasattr(self, '_cached_from_obj'):
            ct = self.relationship.from_content_type
            self._cached_from_obj = ct.get_object_for_this_type(pk=self.from_pk)
        return self._cached_from_obj
    
    @property
    def to_object(self):
        if not hasattr(self, '_cached_to_obj'):
            ct = self.relationship.to_content_type
            self._cached_to_obj = ct.get_object_for_this_type(pk=self.to_pk)
        return self._cached_to_obj


def _connection_created_handler(sender, instance, raw, created, **kwargs):
    if not raw and created:
        connection_created.send(sender=instance.relationship, connection=instance)
post_save.connect(_connection_created_handler, sender=Connection, weak=False)


def _connection_removed_handler(sender, instance, **kwargs):
    connection_removed.send(sender=instance.relationship, connection=instance)
post_delete.connect(_connection_removed_handler, sender=Connection, weak=False)
