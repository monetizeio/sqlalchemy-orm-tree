#!/usr/bin/env python
# -*- coding: utf-8 -*-

# === sqlalchemy_tree.manager.instance ------------------------------------===
# Copyright © 2011-2012, RokuSigma Inc. and contributors. See AUTHORS for more
# details.
#
# Some rights reserved.
#
# Redistribution and use in source and binary forms of the software as well as
# documentation, with or without modification, are permitted provided that the
# following conditions are met:
#
#  * Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#  * The names of the copyright holders or contributors may not be used to
#    endorse or promote products derived from this software without specific
#    prior written permission.
#
# THIS SOFTWARE AND DOCUMENTATION IS PROVIDED BY THE COPYRIGHT HOLDERS AND
# CONTRIBUTORS “AS IS” AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT
# NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE AND
# DOCUMENTATION, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# ===----------------------------------------------------------------------===

# ===----------------------------------------------------------------------===
# This file is based on two BSD-licensed open source projects, SQLAMP and
# Django MPTT. The copyright of the original code is held by its respective
# authors, and the license for each is included below. The work of merging
# these two projects and the continuing work that goes into improvements and
# bug fixes is under copyright held by RokuSigma Inc. and other contributors,
# and distributed under the terms of the three-clause BSD license as described
# above. ALL THREE LICENSE APPLY TO THIS WORK AND ALL AND DERIVED WORKS.
# ===----------------------------------------------------------------------===

# ===----------------------------------------------------------------------===
# SQLAMP
#
# Copyright 2009 Anton Gritsay <anton@angri.ru>
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
# NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
# THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# ===----------------------------------------------------------------------===

# ===----------------------------------------------------------------------===
# Django MPTT
#
# Copyright (c) 2007, Jonathan Buchanan
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# ===----------------------------------------------------------------------===

"A custom manager for working with trees of objects relative to a particular node."

# Python standard library, garbage collection
import weakref

# SQLAlchemy object-relational mapper and SQL expression language
import sqlalchemy

from sqlalchemy_tree.exceptions import InvalidMoveError

from .class_ import TreeClassManager

__all__ = (
  'TreeInstanceManager',
)

# ===----------------------------------------------------------------------===

# FIXME: There's a lot of explicit asserts in here, carried over from the
#        SQLAlchemy code. Because asserts can be ignored in production mode,
#        asserting introduces a distinction between production, development,
#        and testing environments, and should be avoided. These asserts shoud
#        all be either changed into explicit checks which raise exceptions, or
#        removed entirely on case by case basis.

class TreeInstanceManager(TreeClassManager):
  """A node manager, unique for each node instance. Created on first access to
  :class:`TreeManager` descriptor from instance. Implements API to query nodes
  related somehow to a particular node: descendants, ancestors, etc.

  :param class_manager:
    the :class:`TreeClassManager` associated with the node class, which is
    used to perform tree-altering behaviors.
  :param obj:
    particular node instance.
  """
  __slots__ = ('_tree_options', '_obj_ref', 'class_manager', 'node_class',
               'mapper_extension', 'session_extension')
  def __init__(self, class_manager, obj, *args, **kwargs):
    kwargs.setdefault('options',           class_manager._tree_options)
    kwargs.setdefault('node_class',        class_manager.node_class)
    kwargs.setdefault('mapper_extension',  class_manager.mapper_extension)
    kwargs.setdefault('session_extension', class_manager.session_extension)
    super(TreeInstanceManager, self).__init__(*args, **kwargs)
    # The object is stored behind a weakref so that the Python interpreter
    # does the right thing and garbage collects the object if the only pointer
    # to it is this cached instance manager's _obj_ref field.
    self._obj_ref      = weakref.ref(obj)
    self.class_manager = class_manager

  @property
  def pk(self):
    return getattr(self._get_obj(), self._tree_options.pk_field.name)

  @property
  def parent_id(self):
    return getattr(self._get_obj(), self._tree_options.parent_id_field.name)

  @property
  def parent(self):
    return getattr(self._get_obj(), self._tree_options.parent_field_name)

  @property
  def tree_id(self):
    return getattr(self._get_obj(), self._tree_options.tree_id_field.name)

  @property
  def left(self):
    return getattr(self._get_obj(), self._tree_options.left_field.name)

  @property
  def right(self):
    return getattr(self._get_obj(), self._tree_options.right_field.name)

  @property
  def depth(self):
    return getattr(self._get_obj(), self._tree_options.depth_field.name)

  def filter_root_node(self):
    """Return a filter condition identifying the root node of the tree which
    includes this node."""
    return self.filter_root_node_of_node(self._get_obj())

  def query_root_node(self):
    """Return a query containing the root node of the tree which includes this
    node."""
    return self.query_root_node_of_node(self._get_obj())

  @property
  def root_node(self):
    "Return the root node of the tree which includes this node."
    return self.query_root_node_of_node(self._get_obj()).one()

  def filter_ancestors(self, include_self=False):
    "The same as :meth:`filter_descendants` but filters ancestor nodes."
    return self.filter_ancestors_of_node(self._get_obj(), include_self=include_self)

  def query_ancestors(self, session=None, include_self=False):
    "The same as :meth:`query_descendants` but queries node's ancestors."
    return self.query_ancestors_of_node(self._get_obj(), session=session, include_self=include_self)

  def filter_parent(self):
    "Get a filter condition for a node's parent."
    return self.filter_parent_of_node(self._get_obj())

  def filter_siblings(self, include_self=False):
    "Get a filter condition for a node's siblings."
    return self.filter_siblings_of_node(self._get_obj(), include_self=include_self)

  def query_siblings(self, session=None, include_self=False):
    "Get a query containing a nodes siblings."
    return self.query_siblings_of_node(self._get_obj(), session=session, include_self=include_self)

  def filter_previous_siblings(self, include_self=False):
    "Get a filter condition for the siblings of a node which occur prior to it in tree ordering."
    return self.filter_previous_siblings_of_node(self._get_obj(), include_self=include_self)

  def query_previous_siblings(self, session=None, include_self=False):
    "Get a query containing the siblings of a node which occur prior to it in tree ordering."
    return self.query_previous_siblings_of_node(self._get_obj(), session=session, include_self=include_self)

  def filter_next_siblings(self, include_self=False):
    "Get a filter condition for the siblings of a node which occur subsequent to it in tree ordering."
    return self.filter_next_siblings_of_node(self._get_obj(), include_self=include_self)

  def query_next_siblings(self, session=None, include_self=False):
    "Get a query containing the siblings of a node which occur subsequent to it in tree ordering."
    return self.query_next_siblings_of_node(self._get_obj(), session=session, include_self=include_self)

  @property
  def previous_sibling(self):
    "Returns the previous sibling with respect to tree ordering, or `None`."
    if self.is_root_node:
      ordering = sqlalchemy.sql.expression.desc(self.tree_id_field)
    else:
      ordering = sqlalchemy.sql.expression.desc(self.left_field)
    return self.query_previous_siblings().order_by(ordering).first()

  @property
  def next_sibling(self):
    "Returns the next sibling with respect to tree ordering, or `None`."
    if self.is_root_node:
      ordering = sqlalchemy.sql.expression.asc(self.tree_id_field)
    else:
      ordering = sqlalchemy.sql.expression.asc(self.left_field)
    return self.query_next_siblings().order_by(ordering).first()

  def filter_children(self):
    """The same as :meth:`filter_descendants` but filters direct children only
    and does not accept an :attr:`include_self` parameter."""
    return self.filter_children_of_node(self._get_obj())

  def query_children(self, session=None):
    """The same as :meth:`query_descendants` but queries direct children only
    and does not accept an :attr:`include_self` parameter."""
    return self.query_children_of_node(self._get_obj(), session=session)

  def filter_descendants(self, include_self=False):
    """Get a filter condition for node's descendants.

    Requires that node has `tree_id`, `left`, `right` and `depth` values
    available (that means it has “persistent version” even if the node itself
    is in “detached” state or it is in “pending” state in `autoflush`-enabled
    session).

    Usage example::

      session.query(Node).filter(root.mp.filter_descendants()) \\
                         .order_by(Node.mp)

    This example is silly and meant only to illustrate the syntax for using
    `filter_descendants`, don't use it for such purpose as there is a better
    way for such simple queries: :meth:`query_descendants`.

    :param include_self:
      `bool`, if set to `True`, include this node in the filter as well.
    :return:
      a filter clause applicable as argument for
      `sqlalchemy.orm.Query.filter()` and others.
    """
    return self.filter_descendants_of_node(self._get_obj(), include_self=include_self)

  def query_descendants(self, session=None, include_self=False):
    """Get a query for node's descendants.

    Requires that node is in “persistent” state or in “pending” state in
    `autoflush`-enabled session.

    :param session:
      session object for query. If not provided, node's session is used. If
      node is in “detached” state and :attr:`session` is not provided, query
      will be detached too (will require setting `session` attribute to
      execute).
    :param include_self:
      `bool`, if set to `True` self node will be selected by query.
    :return:
      a `sqlalchemy.orm.Query` object which contains only node's descendants.
    """
    return self.query_descendants_of_node(self._get_obj(), session=session, include_self=include_self)

  def get_descendant_count(self):
    "Returns the number of descendants this node has."
    obj   = self._get_obj()
    pk    = getattr(obj, self.pk_field.name)
    left  = getattr(obj, self.left_field.name)
    right = getattr(obj, self.right_field.name)

    # Make sure that node has been saved:
    if pk is None:
      return 0

    return (right - left - 1) / 2

  def filter_leaf_nodes(self, include_self=False):
    """Creates a filter containing leaf nodes of this node instance.

    Requires that node has `tree_id`, `left`, `right` and `depth` values
    available (that means it has “persistent version” even if the node itself
    is in “detached” state or it is in “pending” state in `autoflush`-enabled
    session).

    :param include_self:
      `bool`, if set to `True`, the filter will also include this node (if it
      is a leaf node).
    """
    return self.filter_leaf_nodes_of_node(self._get_obj(), include_self=include_self)

  def query_leaf_nodes(self, session=None, include_self=False):
    """Returns a query containing leaf nodes of this node instance.

    Requires that node has `tree_id`, `left`, `right` and `depth` values
    available (that means it has “persistent version” even if the node itself
    is in “detached” state or it is in “pending” state in `autoflush`-enabled
    session).

    :param session:
      session object for query. If not provided, node's session is used. If
      node is in “detached” state and :attr:`session` is not provided, query
      will be detached too (will require setting `session` attribute to
      execute).
    :param include_self:
      `bool`, if set to `True`, the filter will also include this node (if it
      is a leaf node).
    :return:
      a `sqlalchemy.orm.Query` object which contains only node's descendants
      which are themselves leaf nodes.
    """
    return self.query_leaf_nodes_of_node(self._get_obj(), session=session, include_self=include_self)

  @property
  def is_root_node(self):
    "Returns `True` if the node has no parent."
    return self.left == 1

  @property
  def is_child_node(self):
    "Returns `True` if the node has a parent."
    return self.left != 1

  @property
  def is_leaf_node(self):
    "Returns `True` if the node has no children."
    return self.left == self.right-1

  def is_ancestor_of(self, descendant, include_self=False):
    "Returns `True` if the passed-in node is a descendant of this node."
    return self.any_ancestors_of(
      descendant, self._get_obj(), include_self=include_self)

  def is_sibling_of(self, sibling, include_self=True):
    "Returns `True` if the passed-in node is a sibling to this node."
    if self.parent_id != getattr(sibling, self.parent_id_field.name):
      return False
    return (include_self and True
                          or self.pk != getattr(sibling, self.pk_field.name))

  def is_child_of(self, parent):
    "Returns `True` if the passed-in node is parent to this node."
    return self.parent_id == getattr(parent, self.pk_field.name)

  def is_descendant_of(self, ancestor, include_self=False):
    "Returns `True` if the passed-in node is an ancestor of this node."
    return self.any_descendants_of(ancestor, self._get_obj(), include_self=include_self)

  def _get_obj(self):
    "Dereference weakref and return node instance."
    return self._obj_ref()

  def _get_query(self, obj, session):
    """Get a `Query` object for this node's class, using the specified
    session. If :attr:`session` is `None`, tries to use :attr:`obj`'s session
    if it is available.

    :param session:
      a sqlalchemy `Session` instance or `None`.
    :return:
      a `sqlalchemy.orm.Query` instance.
    :raises AssertionError:
      if :attr:`session` is `None` and node is not bound to a session.
    """
    # Get the session containing the object, flushing it (if necessary) so as
    # to generate values for the tree fields if they don't already exist:
    obj_session = self._get_session_and_assert_flushed(obj)

    # Use object's session only if particular session was not specified:
    if session is None:
      session = obj_session

    # Have SQLAlchemy generate and return a new query object:
    return sqlalchemy.orm.Query(self.node_class, session=session)

  # FIXME: For some operations, `_get_session_and_assert_flushed` is called
  #        more than once by various layers in the call stack. This doesn't
  #        cause problems, but it is inefficient. We should figure out how to
  #        avoid that.
  def _get_session_and_assert_flushed(self, obj):
    """Ensure that node has “real” values in its `tree_id`, `left`, `right`
    and `depth` fields, and return node's session.

    Determines object session, flushs it if instance is in “pending” state and
    session has `autoflush == True`. Flushing is needed for the instance's
    `tree_id`, `left`, `right`, and `depth` fields to hold actual values. If
    the node is not bound to a session, we try to check that it was
    “persistent” once upon a time.

    :return:
      session object or `None` if node is in “detached” state.
    :raises AssertionError:
      if instance is in “pending” state and session has `autoflush` disabled.
    :raises AssertionError:
      if instance is in “transient” state (has no “persistent” copy and is not
      bound to a session).
    """
    # SQLAlchemy's object_sesion() function takes care of the magic of finding
    # the session object associated with our passed-in object:
    session = sqlalchemy.orm.session.object_session(obj)

    # If the object is newly created, the session needs to be flushed in order
    # for its tree fields to be populated with actual values. We detect this
    # case while being careful to protect the semantics of the autoflush
    # configuration:
    if session is not None:
      if obj in session.new:
        assert session.autoflush, \
              (u"instance %r is in “pending” state and attached to non-" \
               u"autoflush session. call `session.flush()` to be able to " \
               u"get filters and perform queries.") % obj
        session.flush()

    # Otherwise we make sure that each of the tree fields have been specified,
    # even though the object is not yet part of a session:
    else:
      assert all(getattr(obj, field.name) is not None \
                 for field in self._tree_options.required_fields), \
            (u"instance %r seems to be in “transient” state. put it in the " \
             u"session to be able to get filters and perform queries.") % obj

    # Return the session object (or None):
    return session

# ===----------------------------------------------------------------------===
# End of File
# ===----------------------------------------------------------------------===
