from django import template

from ..models import get_relationship


register = template.Library()


@register.assignment_tag
def get_connection_distance(relationship, obj1, obj2, limit=2):
    """
    Calculates the distance between the two given objects for the given
    relationship. See `connections.models.Relationship` for more info.
    
        {% get_connection_distance 'relationship_name' obj1 obj2 as distance %}
        {% get_connection_distance 'relationship_name' obj1 obj2 limit=3 as distance %}
    
    """
    return get_relationship(relationship).distance_between(obj1, obj2, limit)


@register.assignment_tag
def connections_from_object(relationship, obj1):
    """
        {% connections_from_object 'relationship_name' obj1 as connections %}
    """
    return get_relationship(relationship).connections_from_object(obj1)


@register.assignment_tag
def connections_to_object(relationship, obj1):
    """
        {% connections_to_object 'relationship_name' obj1 as connections %}
    """
    return get_relationship(relationship).connections_to_object(obj1)


@register.assignment_tag
def connection_exists(relationship, obj1, obj2):
    """
        {% connection_exists 'relationship_name' obj1 obj2 as connections %}
    """
    return get_relationship(relationship).connection_exists(obj1, obj2)
