
def define_relationship(name, from_model, to_model):
    from .models import define_relationship as _define_relationship
    return _define_relationship(name, from_model, to_model)


def get_relationship(name):
    from .models import get_relationship as _get_relationship
    return _get_relationship(name)


def get_connection(relationship, from_obj, to_obj):
    from .models import get_relationship
    return get_relationship(relationship).get_connection(from_obj, to_obj)


def create_connection(relationship, from_obj, to_obj):
    from .models import get_relationship
    return get_relationship(relationship).create_connection(from_obj, to_obj)


def connection_exists(relationship, from_obj, to_obj):
    from .models import get_relationship
    return get_relationship(relationship).connection_exists(from_obj, to_obj)


def connections_from_object(relationship, from_obj):
    from .models import get_relationship
    return get_relationship(relationship).connections_from_object(from_obj)


def connections_to_object(relationship, to_obj):
    from .models import get_relationship
    return get_relationship(relationship).connections_to_object(to_obj)


def connected_objects(relationship, from_obj):
    from .models import get_relationship
    return get_relationship(relationship).connected_objects(from_obj)


def connected_to_objects(relationship, to_obj):
    from .models import get_relationship
    return get_relationship(relationship).connected_to_objects(to_obj)
