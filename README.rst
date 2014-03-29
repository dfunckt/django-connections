django-connections
^^^^^^^^^^^^^^^^^^

.. image:: https://travis-ci.org/dfunckt/django-connections.svg?branch=master
    :target: https://travis-ci.org/dfunckt/django-connections
.. image:: https://coveralls.io/repos/dfunckt/django-connections/badge.png?branch=master
    :target: https://coveralls.io/r/dfunckt/django-connections?branch=master

``connections`` is a small app for Django that allows you to model any kind of
relationship between instances of *any* model. It's primary use is for
building a social graph that you can query and manage easily.


Requirements
============

``connections`` requires Python 2.6/3.2 or newer and Django 1.5 or newer.


How to install
==============

Using pip::

    $ pip install django-connections

Manually::

    $ git clone https://github.com/dfunckt/django-connections.git
    $ cd django-connections
    $ python setup.py install


Configuration
=============

Add ``connections`` to your settings::

    INSTALLED_APPS = (
        # ...
        'connections',
    )

Then, run ``migrate``::

    $ python manage.py migrate

**Note**: If you're running Django 1.6 or lower, you should run
``manage.py syncdb`` instead.


Using ``connections``
=====================

With ``connections`` you essentially build `directed graphs`_, where each
*node* is a model instance and each *edge* is a ``Connection`` instance. Which
two models a connection can connect, is determined by a ``Relationship``
instance that you predefine.

.. _directed graphs: http://wikipedia.org/wiki/Directed_graph


Defining relationships
----------------------

Assume you're *LitHub*, a social coding site in its infancy, and you need to
let your users star repositories they find interesting. With ``connections``,
you would first define a relationship::

    >>> from django.contrib.auth.models import User
    >>> from connections import define_relationship
    >>> from lithub.models import Repo
    >>> repo_stars = define_relationship('star_repo', from_model=User, to_model=Repo)

``define_relationship`` creates and registers a new ``Relationship`` instance
between the given models, with the name ``'star_repo'``. Names of
relationships must be unique across your project. You may alternatively
specify the models of the relationship as strings, e.g. ``'auth.User'`` or
``'lithub.Repo'``.

Any time you need to reference a relationship, you can either import the
module variable (as defined above), or use ``connections.get_relationship(name)``.


Managing connections
--------------------

Let's say that ``milo`` found a nice Python project on LitHub that he'd like
to star, for future reference. In ``connections`` this can be modelled by
creating a connection between ``milo`` and the repository instance::

    >>> milo = User.objects.get(pk=104)
    >>> foopy = Repo.objects.get(pk=47)
    >>> star_repo.create_connection(milo, foopy)
    'star_repo (auth.User:104 -> lithub.Repo:47)'

Connections are unidirectional, meaning that if *foo* is connected with
*bar*, the reverse -- that *bar* is connected to *foo* -- is *not* implied.
If you'd like to model a symmetrical relationship, that is, one that only
makes sense if both sides have agreed in the relationship (e.g. *friendship*
or even *marriage*), you'd have to create two opposite connections, one for
each side of the relationship.

Let's see what repositories ``milo`` has starred::

    >>> repo_stars.connected_objects(milo)
    [<Repo: foopy>]

We can also query for the reverse, that is, what users have starred ``foopy``::

    >>> repo_stars.connected_to_objects(foopy)
    [<User: milo>]

There are several other methods you may use to query or manage connections,
that you may read about in `API Reference`_.


Best practices
==============

The preferred idiom is to define relationships in ``app/relationships.py``
files, keeping a module-global reference to each relationship instance,
through which you manage connections between your model instances.

If you're using Django 1.7 or later you may have any ``relationships.py``
modules automatically imported at start-up::

    INSTALLED_APPS = (
        # ...
        'connections.apps.AutodiscoverConnectionsConfig',
    )


API Reference
=============


Class ``Relationship``
----------------------

Represents a predefined type of connection between two nodes in a (directed)
graph. You may imagine relationships as the *kind* of an edge in the graph.
::

    >>> from connections.models import Relationship
    >>> rel = Relationship('rel_name', from_content_type, to_content_type)


Instance properties
+++++++++++++++++++

``connections``
    Returns a ``Connection`` query set matching all connections of this
    relationship.


Instance methods
++++++++++++++++

``create_connection(from_obj, to_obj)``
    Creates and returns a new ``Connection`` instance between the given
    objects. If a connection already exists, the existing connection will be
    returned instead of creating a new one.

``get_connection(from_obj, to_obj)``
    Returns a ``Connection`` instance for the given objects or ``None`` if
    there's no connection.

``connection_exists(from_obj, to_obj)``
    Returns ``True`` if a connection between the given objects exists,
    else ``False``.

``connections_from_object(from_obj)``
    Returns a ``Connection`` query set matching all connections with
    the given object as a source.

``connections_to_object(to_obj)``
    Returns a ``Connection`` query set matching all connections with
    the given object as a destination.

``connected_objects(from_obj)``
    Returns a query set matching all connected objects with the given
    object as a source.

``connected_object_ids(from_obj)``
    Returns an iterable of the IDs of all objects connected with the given
    object as a source (i.e. the ``Connection.to_pk`` values).

``connected_to_objects(to_obj)``
    Returns a query set matching all connected objects with the given
    object as a destination.

``connected_to_object_ids(to_obj)``
    Returns an iterable of the IDs of all objects connected with the given
    object as a destination (i.e. the ``Connection.from_pk`` values).

``distance_between(from_obj, to_obj, limit=2)``
    Calculates and returns an integer for the distance between two objects.
    A distance of *0* means ``from_obj`` and ``to_obj`` are the same
    objects, *1* means ``from_obj`` has a direct connection to ``to_obj``,
    *2* means that one or more of ``from_obj``'s connected objects are
    directly connected to ``to_obj``, and so on. ``limit`` limits the depth of
    connections traversal. Returns ``None`` if the two objects are not
    connected within ``limit`` distance.


Class ``Connection``
--------------------

Represents a connection between two nodes in the graph. Connections must
be treated as unidirectional, i.e. creating a connection from one node to
another should not imply the reverse.


Model attributes
++++++++++++++++

``relationship_name``
    The name of the relationship. To access the relationship instance, use the
    ``Connection.relationship`` property.

``from_pk``
    The primary key of the instance acting as source.

``to_pk``
    The primary key of the instance acting as destination.

``date``
    A ``datetime`` instance of the time the connection was created.


Instance properties
+++++++++++++++++++

``relationship``
    Returns the ``Relationship`` instance the connection is about.

``from_object``
    The source instance.

``to_object``
    The destination instance.
