#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    sqlalchemy_tree
    ~~~~~~~~~~~~~~~

    An implementation for SQLAlchemy-based applications of the
    nested-sets/modified-pre-order-tree-traversal technique for storing
    hierarchical data in a relational database.

    :copyright: (C) 2012-2014 the SQLAlchemy-ORM-Tree authors and contributors
                <see AUTHORS file>
    :license: BSD, see LICENSE for more details.
"""

from operator import attrgetter

from .exceptions import InvalidMoveError
from .manager import TreeClassManager, TreeInstanceManager, TreeManager
from .options import TreeOptions
from .orm import TreeMapperExtension, TreeSessionExtension
from .types import TreeDepthType, TreeEndpointType, TreeIdType, \
    TreeIntegerType, TreeLeftType, TreeRightType

from . import tests


_nonexistent = object()
def _iter_current_next(sequence):
    """
    Generate `(current, next)` tuples from sequence. Last tuple will
    have `_nonexistent` object at the second place.

    >>> x = _iter_current_next('1234')
    >>> next(x), next(x), next(x)
    (('1', '2'), ('2', '3'), ('3', '4'))
    >>> next(x) == ('4', _nonexistent)
    True
    >>> list(_iter_current_next(''))
    []
    >>> list(_iter_current_next('1')) == [('1', _nonexistent)]
    True
    """
    iterator = iter(sequence)
    current_item = next(iterator)
    while current_item != _nonexistent:
        try:
            next_item = next(iterator)
        except StopIteration:
            next_item = _nonexistent
        yield (current_item, next_item)
        current_item = next_item


def _recursive_iterator(sequence, is_child_func):
    """
    Make a recursive iterator from plain sequence using :attr:`is_child_func`
    to determine parent-children relations. Works right only if used in
    depth-first recursive consumer.

    :param is_child_func:
        a callable object which accepts two positional arguments and
        returns `True` value if first argument value is parent of second
        argument value.

    >>> is_child_func = lambda parent, child: child > parent
    >>> def listify(seq):
    ...     return [(node, listify(children)) for node, children in seq]
    >>> listify(_recursive_iterator('ABCABB', is_child_func))
    [('A', [('B', [('C', [])])]), ('A', [('B', []), ('B', [])])]
    >>> listify(_recursive_iterator('', is_child_func))
    []
    >>> next(_recursive_iterator('A', is_child_func))
    ('A', ())
    >>> next(_recursive_iterator('AB', is_child_func)) # doctest: +ELLIPSIS
    ('A', <generator object ...>)
    """
    current_next_iterator = _iter_current_next(sequence)
    item = {}
    is_parent_of_next = lambda node: \
            item['next'] is not _nonexistent \
            and is_child_func(node, item['next'])

    def step():
        item['current'], item['next'] = next(current_next_iterator)
        if is_parent_of_next(item['current']):
            return (item['current'], children_generator(item['current']))
        else:
            return (item['current'], tuple())

    def children_generator(parent_node):
        while True:
            yield step()
            if not is_parent_of_next(parent_node):
                break

    while True:
        yield step()


def tree_recursive_iterator(flat_tree, class_manager):
    """
    Make a recursive iterator from plain tree nodes sequence (`Query`
    instance for example). Generates two-item tuples: node itself
    and it's children collection (which also generates two-item tuples...)
    Children collection evaluates to ``False`` if node has no children
    (it is zero-length tuple for leaf nodes), else it is a generator object.

    :param flat_tree: plain sequence of tree nodes.
    :param class_manager: instance of :class:`MPClassManager`.

    Can be used when it is simpler to process tree structure recursively.
    Simple usage example::

        def recursive_tree_processor(nodes):
            print '<ul>'
            for node, children in nodes:
                print '<li>%s' % node.name,
                if children:
                    recursive_tree_processor(children)
                print '</li>'
            print '</ul>'

        query = root_node.mp.query_descendants(and_self=True)
        recursive_tree_processor(
            sqlamp.tree_recursive_iterator(query, Node.mp)
        )

    .. versionchanged::
        0.6
        Before this function was sorting `flat_tree` if it was a query-object.
        Since 0.6 it doesn't do it, so make sure that `flat_tree` is properly
        sorted. The best way to achieve this is using queries returned from
        public API methods of :class:`MPClassManager` and
        :class:`MPInstanceManager`.

    .. warning:: Process `flat_tree` items once and sequentially so works
      right only if used in depth-first recursive consumer.
    """
    opts = class_manager._tree_options
    tree_id = attrgetter(opts.tree_id_field.name)
    depth = attrgetter(opts.depth_field.name)
    def is_child(parent, child):
        return tree_id(parent) == tree_id(child) \
                and depth(child) == depth(parent) + 1
    return _recursive_iterator(flat_tree, is_child)
