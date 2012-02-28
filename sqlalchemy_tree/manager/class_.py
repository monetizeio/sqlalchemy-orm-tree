#!/usr/bin/env python
# -*- coding: utf-8 -*-

# === sqlalchemy_tree.manager.class_ --------------------------------------===
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

# SQLAlchemy object-relational mapper and SQL expression language
import sqlalchemy

class TreeClassManager(object):
  """Node class manager, which handles tree-wide operations such as insertion,
  deletion, and moving nodes around. No need to create it by hand: it is
  created by :class:``TreeManager``.

  :param node_class:
    class which was mapped to tree table.
  :param options:
    instance of :class:``TreeOptions``
  """
  def __init__(self, node_class, options, mapper_extension, session_extension):
    # Save our parameters for future use:
    self._tree_options     = options
    self.node_class        = node_class
    self.mapper_extension  = mapper_extension
    self.session_extension = session_extension

  def __clause_element__(self):
    """Allows to use instances of ``TreeClassManager`` directly as argument
    for ``sqlalchemy.orm.Query.order_by()`` to efficiently order a query into
    preorder traversal ordering (sort by first ``tree_id`` and then ``left``
    fields). Can be used like this (assume that :class:``TreeManager`` is
    attached to class ``Node`` and named ``'tree'``)::

      query = root.query_children()
      query.order_by(Node.tree)
    """
    return self._tree_options.order_by_clause()

  def register(self):
    ""
    options = self._tree_options

    if not getattr(options, '_event_listeners', False):
      setattr(options, '_event_listeners', True)
      sqlalchemy.event.listen(sqlalchemy.orm.session.Session,
                              'before_flush',
                              self.session_extension.before_flush)
      sqlalchemy.event.listen(self.node_class,
                              'before_insert',
                              self.mapper_extension.before_insert)
      sqlalchemy.event.listen(self.node_class,
                              'after_insert',
                              self.mapper_extension.after_insert)
      sqlalchemy.event.listen(self.node_class,
                              'before_delete',
                              self.mapper_extension.before_delete)
      sqlalchemy.event.listen(self.node_class,
                              'after_delete',
                              self.mapper_extension.after_delete)
      sqlalchemy.event.listen(self.node_class,
                              'before_update',
                              self.mapper_extension.before_update)
      sqlalchemy.event.listen(self.node_class,
                              'after_update',
                              self.mapper_extension.after_update)

  @property
  def pk_field(self):
    return self._tree_options.pk_field

  @property
  def parent_id_field(self):
    return self._tree_options.parent_id_field

  @property
  def parent_field_name(self):
    return self._tree_options.parent_field_name

  @property
  def tree_id_field(self):
    return self._tree_options.tree_id_field

  @property
  def left_field(self):
    return self._tree_options.left_field

  @property
  def right_field(self):
    return self._tree_options.right_field

  @property
  def depth_field(self):
    return self._tree_options.depth_field

  def filter_root_nodes(self):
    "Get a filter condition for all root nodes."
    # We avoid using the adjacency-list parent field because that column may
    # or may not be indexed. The ``left`` field is always 1 on a root node,
    # and we know an index exists on that field.
    return self.left_field == 1

  def query_root_nodes(self, session=None, *args, **kwargs):
    """Convenience method that gets a query for all root nodes using
    ``filter_root_nodes`` and the session associated with this node. The
    session must be passed explicitly if called from a class manager."""
    if session is None:
      # NOTE: ``self._get_obj`` only exists on instance managers--session may
      #       only be ``None`` if called from an instance manager of a node
      #       associated with a session.
      session = sqlalchemy.orm.object_session(self._get_obj())
    return session.query(self.node_class) \
                  .filter(self.filter_root_nodes(*args, **kwargs))

  def filter_root_node_by_tree_id(self, *args):
    """Get a filter condition returning root nodes of the tree specified
    through the positional arguments (interpreted as tree ids)."""
    return self.filter_root_nodes() & \
           self.tree_id_field.in_(args)

  def query_root_node_by_tree_id(self, *args, **kwargs):
    """Returns the root nodes of the trees specified through the positional
    arguments (interpreted as tree ids) using ``filter_root_node_by_tree_id``
    and the session associated with this node. The session must be passed
    explicitly if called from a class manager."""
    session = kwargs.pop('session', None)
    if session is None:
      # NOTE: ``self._get_obj`` only exists on instance managers--session may
      #       only be ``None`` if called from an instance manager of a node
      #       associated with a session.
      session = sqlalchemy.orm.object_session(self._get_obj())
    return session.query(self.node_class) \
                  .filter(self.filter_root_node_by_tree_id(*args, **kwargs))

  def filter_root_node_of_node(self, *args):
    """Get a filter condition returning the root nodes of the trees which
    include the passed-in nodes."""
    return self.filter_root_nodes() & \
           self.tree_id_field.in_(
             set(map(lambda n:getattr(n, self.tree_id_field.name), args)))

  def query_root_node_of_node(self, *args, **kwargs):
    """Returns the root nodes of the trees which contain the passed in nodes,
    using ``filter_root_node_by_tree_id``. The session used to perform the
    query is either a) the session explicitly passed in, b) the session
    associated with the first bound positional parameter, or c) the session
    associated with the instance manager's node."""
    session = kwargs.pop('session', None)
    if session is None:
      session = self._get_session_from_args_or_self(*args)
    return session.query(self.node_class) \
                  .filter(self.filter_root_node_of_node(*args, **kwargs))

  def filter_ancestors_of_node(self, *args, **kwargs):
    "Returns a filter condition for the ancestors of passed-in nodes."
    options      = self._tree_options
    include_self = kwargs.pop('include_self', False) # Include self in results
    disjoint     = kwargs.pop('disjoint',     True)  # Logical-AND vs. -OR for reduction
    for extra in kwargs:
      raise TypeError, u"unexpected keyword argument '%s'" % extra

    def _filter_ancestors_of_node_helper(node):
      # Restrict ourselves to just those nodes within the same tree as node:
      tree_id = getattr(node, self.tree_id_field.name)
      filter_ = self.tree_id_field == tree_id

      # Restrict to ancestors, inclusive of node:
      alias = sqlalchemy.alias(options.table)
      left_field = self.left_field
      filter_ &= sqlalchemy.between(
        getattr(alias.c, self.left_field.name),
        self.left_field, self.right_field)
      filter_ &= getattr(alias.c, self.pk_field.name) == \
                 getattr(node,    self.pk_field.name)

      # Explicitly exclude node, if requested:
      if not include_self:
        filter_ &= self.pk_field != getattr(node, self.pk_field.name)

      # We're done!
      return filter_

    # Combine SQL expression clauses into a clause identifying the combined
    # ancestors of each node in turn, according to the requested behavior in
    # handling disjoint sets (logical-OR/union vs. logical-AND/intersection):
    filters = map(_filter_ancestors_of_node_helper, args)
    if disjoint:
      return reduce(lambda l,r: l | r, filters)
    else:
      return reduce(lambda l,r: l & r, filters)

  def query_ancestors_of_node(self, *args, **kwargs):
    "Returns a query containing the ancestors of passed-in nodes."
    session = kwargs.pop('session', None)
    if session is None:
      session = self._get_session_from_args_or_self(*args)
    return session.query(self.node_class) \
                  .filter(self.filter_ancestors_of_node(*args, **kwargs))

  def filter_parent_of_node(self, *args):
    "Get a filter condition for the parents of passed-in nodes."
    parent_ids = filter(
      lambda parent_id:parent_id is not None,
      map(
        lambda node:getattr(node, self.parent_id_field.name), args))
    return self.pk_field.in_(parent_ids)

  def query_parent_of_node(self, *args, **kwargs):
    "Returns a query containing the parents of passed-in nodes."
    session = kwargs.pop('session', None)
    if session is None:
      session = self._get_session_from_args_or_self(*args)
    return session.query(self.node_class) \
                  .filter(self.filter_parent_of_node(*args, **kwargs))

  def filter_siblings_of_node(self, *args, **kwargs):
    "Returns a filter condition identifying siblings of passed-in nodes."
    include_self = kwargs.pop('include_self', False) # Include self in results
    disjoint     = kwargs.pop('disjoint',     True)  # Logical-AND vs. -OR for reduction
    for extra in kwargs:
      raise TypeError, u"unexpected keyword argument '%s'" % extra

    def _filter_siblings_of_node_helper(node):
      pk        = getattr(node, self.pk_field.name)
      parent_id = getattr(node, self.parent_id_field.name)

      # Restrict to siblings via the parent_id value:
      filter_ = self.parent_id_field == parent_id

      # Explicitly exclude node, if requested:
      if not include_self:
        filter_ &= self.pk_field != pk

      # We're done!
      return filter_

    # Combine SQL expression clauses into a clause identifying the combined
    # ancestors of each node in turn, according to the requested behavior in
    # handling disjoint sets (logical-OR/union vs. logical-AND/intersection):
    filters = map(_filter_siblings_of_node_helper, args)
    if disjoint:
      return reduce(lambda l,r: l | r, filters)
    else:
      return reduce(lambda l,r: l & r, filters)

  def query_siblings_of_node(self, *args, **kwargs):
    "Returns a query containing the siblings of passed-in nodes."
    session = kwargs.pop('session', None)
    if session is None:
      session = self._get_session_from_args_or_self(*args)
    return session.query(self.node_class) \
                  .filter(self.filter_siblings_of_node(*args, **kwargs))

  def filter_previous_siblings_of_node(self, *args, **kwargs):
    "Returns a filter condition identifying siblings to the left of passed-in nodes."
    include_self = kwargs.pop('include_self', False) # Include self in results
    disjoint     = kwargs.pop('disjoint',     True)  # Logical-AND vs. -OR for reduction
    for extra in kwargs:
      raise TypeError, u"unexpected keyword argument '%s'" % extra

    def _filter_previous_siblings_of_node_helper(node):
      pk        = getattr(node, self.pk_field.name)
      parent_id = getattr(node, self.parent_id_field.name)

      # Restrict to siblings via the parent_id value:
      filter_ = self.parent_id_field == parent_id

      if parent_id is None:
        # Restrict to the specified root node and those with lower `tree_id` values:
        filter_ &= self.tree_id_field <= getattr(node, self.tree_id_field.name)
      else:
        # Restrict to the specified child node and those with lower `left` values:
        filter_ &= self.left_field <= getattr(node, self.left_field.name)

      # Explicitly exclude node, if requested:
      if not include_self:
        filter_ &= self.pk_field != pk

      # We're done!
      return filter_

    # Combine SQL expression clauses into a clause identifying the combined
    # ancestors of each node in turn, according to the requested behavior in
    # handling disjoint sets (logical-OR/union vs. logical-AND/intersection):
    filters = map(_filter_previous_siblings_of_node_helper, args)
    if disjoint:
      return reduce(lambda l,r: l | r, filters)
    else:
      return reduce(lambda l,r: l & r, filters)

  def query_previous_siblings_of_node(self, *args, **kwargs):
    "Returns a query containing siblings to the left of passed-in nodes."
    session = kwargs.pop('session', None)
    if session is None:
      session = self._get_session_from_args_or_self(*args)
    return session.query(self.node_class) \
                  .filter(self.filter_previous_siblings_of_node(*args, **kwargs))

  def filter_next_siblings_of_node(self, *args, **kwargs):
    "Returns a filter condition identifying siblings to the right of passed-in nodes."
    include_self = kwargs.pop('include_self', False) # Include self in results
    disjoint     = kwargs.pop('disjoint',     True)  # Logical-AND vs. -OR for reduction
    for extra in kwargs:
      raise TypeError, u"unexpected keyword argument '%s'" % extra

    def _filter_next_siblings_of_node_helper(node):
      pk        = getattr(node, self.pk_field.name)
      parent_id = getattr(node, self.parent_id_field.name)
      left      = getattr(node, self.left_field.name)

      # Restrict to siblings via the parent_id value:
      filter_ = self.parent_id_field == parent_id

      if parent_id is None:
        # Restrict to the specified root node and those with higher `tree_id` values:
        filter_ &= self.tree_id_field >= getattr(node, self.tree_id_field.name)
      else:
        # Restrict to the specified child node and those with higher `left` values:
        filter_ &= self.left_field >= getattr(node, self.left_field.name)

      # Explicitly exclude node, if requested:
      if not include_self:
        filter_ &= self.pk_field != pk

      # We're done!
      return filter_

    # Combine SQL expression clauses into a clause identifying the combined
    # ancestors of each node in turn, according to the requested behavior in
    # handling disjoint sets (logical-OR/union vs. logical-AND/intersection):
    filters = map(_filter_next_siblings_of_node_helper, args)
    if disjoint:
      return reduce(lambda l,r: l | r, filters)
    else:
      return reduce(lambda l,r: l & r, filters)

  def query_next_siblings_of_node(self, *args, **kwargs):
    "Returns a query containing siblings to the right of passed-in nodes."
    session = kwargs.pop('session', None)
    if session is None:
      session = self._get_session_from_args_or_self(*args)
    return session.query(self.node_class) \
                  .filter(self.filter_next_siblings_of_node(*args, **kwargs))

  def filter_children_of_node(self, *args):
    "Returns a filter condition for the children of passed-in nodes."
    def _filter_children_of_node_helper(node):
      # Since we store the denormalized depth field, this query is pretty
      # easy: just ask for those descendants with the correct depth value.
      depth = getattr(node, self.depth_field.name) + 1

      # Oh yeah, using adjacency relation may be more efficient here. But one
      # can access AL-based children collection without this library at all.
      # And in this case we can be sure that at least the `(tree_id, left,
      # right)` index is used. `parent_id` field may not have index set up so
      # condition `pk == parent_id` in a SQL query could be even less
      # efficient.
      return self.filter_descendants_of_node(node) & (self.depth_field == depth)

    # Combine SQL expression clauses into a clause identifying the combined
    # ancestors of each node in turn, according to the requested behavior in
    # handling disjoint sets (logical-OR/union vs. logical-AND/intersection):
    return reduce(
      lambda l,r: l | r,
      map(_filter_children_of_node_helper, args),
      sqlalchemy.sql.expression.false())

  def query_children_of_node(self, *args, **kwargs):
    "Returns a query containing the children of passed-in nodes."
    session = kwargs.pop('session', None)
    if session is None:
      session = self._get_session_from_args_or_self(*args)
    return session.query(self.node_class) \
                  .filter(self.filter_children_of_node(*args, **kwargs))

  def filter_descendants_of_node(self, *args, **kwargs):
    "Returns a filter condition for the descendants of passed-in nodes."
    include_self = kwargs.pop('include_self', False) # Include self in results
    disjoint     = kwargs.pop('disjoint',     True)  # Logical-AND vs. -OR for reduction
    for extra in kwargs:
      raise TypeError, u"unexpected keyword argument '%s'" % extra

    def _filter_descendants_of_node_helper(node):
      tree_id = getattr(node, self.tree_id_field.name)
      left    = getattr(node, self.left_field.name)
      right   = getattr(node, self.right_field.name) - 1

      # If the caller requests the specified node to be included, this is most
      # easily accomplished by not incrementing left by one, so that the node
      # is now included in the resulting interval:
      left = include_self and left or left + 1

      # Restrict ourselves to just those nodes within the same tree:
      filter_ = self.tree_id_field == tree_id

      # Any node which has a left value between this node's left and right
      # values must be a descendant of this node:
      filter_ &= sqlalchemy.between(self.left_field, left, right)

      # We're done!
      return filter_

    # Combine SQL expression clauses into a clause identifying the combined
    # ancestors of each node in turn, according to the requested behavior in
    # handling disjoint sets (logical-OR/union vs. logical-AND/intersection):
    filters = map(_filter_descendants_of_node_helper, args)
    if disjoint:
      return reduce(lambda l,r: l | r, filters)
    else:
      return reduce(lambda l,r: l & r, filters)

  def query_descendants_of_node(self, *args, **kwargs):
    "Returns a query containing the descendants of passed-in nodes."
    session = kwargs.pop('session', None)
    if session is None:
      session = self._get_session_from_args_or_self(*args)
    return session.query(self.node_class) \
                  .filter(self.filter_descendants_of_node(*args, **kwargs))

  def filter_leaf_nodes(self):
    "Creates a filter condition containing all leaf nodes."
    return self.left_field == (self.right_field-1)

  def query_leaf_nodes(self, session=None, *args, **kwargs):
    "Returns a query containing all leaf nodes."
    if session is None:
      # NOTE: ``self._get_obj`` only exists on instance managers--session may
      #       only be ``None`` if called from an instance manager of a node
      #       associated with a session.
      session = sqlalchemy.orm.object_session(self._get_obj())
    return session.query(self.node_class) \
                  .filter(self.filter_leaf_nodes(*args, **kwargs))

  def filter_leaf_nodes_by_tree_id(self, *args):
    """Creates a filter condition containing all leaf nodes of the tree(s)
    specified through the positional arguments (interpreted as tree ids)."""
    return self.filter_leaf_nodes() & \
           self.tree_id_field.in_(args)

  def query_leaf_nodes_by_tree_id(self, *args, **kwargs):
    """Returns a query containing all leaf nodes of the tree(s) specified
    through the positional arguments (interpreted as tree ids) using
    ``filter_leaf_nodes_by_tree_id`` and the session associated with this
    node. The session must be passed explicitly if called from a class
    manager."""
    session = kwargs.pop('session', None)
    if session is None:
      # NOTE: ``self._get_obj`` only exists on instance managers--session may
      #       only be ``None`` if called from an instance manager of a node
      #       associated with a session.
      session = sqlalchemy.orm.object_session(self._get_obj())
    return session.query(self.node_class) \
                  .filter(self.filter_leaf_nodes_by_tree_id(*args, **kwargs))

  def filter_leaf_nodes_of_node(self, *args, **kwargs):
    """Get a filter condition returning the leaf nodes of the descendants of
    the passed-in nodes."""
    include_self = kwargs.pop('include_self', False) # Include self in results
    disjoint     = kwargs.pop('disjoint',     True)  # Logical-AND vs. -OR for reduction
    for extra in kwargs:
      raise TypeError, u"unexpected keyword argument '%s'" % extra

    def _filter_leaf_nodes_of_node_helper(node):
      tree_id = getattr(node, self.tree_id_field.name)
      left    = getattr(node, self.left_field.name)
      right   = getattr(node, self.right_field.name) - 1

      # If the caller requests the specified node to be included, this is most
      # easily accomplished by not incrementing left by one, so that the node
      # is now included in the resulting interval:
      left = include_self and left or left + 1

      # Restrict ourselves to just those nodes within the same tree:
      filter_ = self.tree_id_field == tree_id

      # Restrict ourselves to leaf nodes...
      filter_ &= self.left_field == (self.right_field-1)

      # ...which are descendants of this node (any node which has a left value
      # between this node's left and right values must be a descendant of this
      # node):
      filter_ &= sqlalchemy.between(self.left_field, left, right)

      # We're done!
      return filter_

    # Combine SQL expression clauses into a clause identifying the combined
    # ancestors of each node in turn, according to the requested behavior in
    # handling disjoint sets (logical-OR/union vs. logical-AND/intersection):
    filters = map(_filter_leaf_nodes_of_node_helper, args)
    if disjoint:
      return reduce(lambda l,r: l | r, filters)
    else:
      return reduce(lambda l,r: l & r, filters)

  def query_leaf_nodes_of_node(self, *args, **kwargs):
    """Returns the leaf nodes of the descendants of the passed-in nodes, using
    ``filter_leaf_nodes_by_tree_id``. The session used to perform the
    query is either a) the session explicitly passed in, b) the session
    associated with the first bound positional parameter, or c) the session
    associated with the instance manager's node."""
    session = kwargs.pop('session', None)
    if session is None:
      session = self._get_session_from_args_or_self(*args)
    return session.query(self.node_class) \
                  .filter(self.filter_leaf_nodes_of_node(*args, **kwargs))

  def any_root_nodes(self, *args):
    "Return `True` if any of the positional arguments are root nodes."
    return reduce(
      lambda l,r: l or r,
      map(
        lambda node: getattr(node, self.parent_id_field.name) is None,
        args))

  def all_root_nodes(self, *args):
    "Return `False` unless every one of the positional arguments is a root node."
    return reduce(
      lambda l,r: l and r,
      map(
        lambda node: getattr(node, self.parent_id_field.name) is None,
        args))

  def any_child_nodes(self, *args):
    "Return `True` if any of the positional arguments are child nodes."
    return reduce(
      lambda l,r: l or r,
      map(
        lambda node: getattr(node, self.parent_id_field.name) is not None,
        args))

  def all_child_nodes(self, *args):
    "Return `False` unless every one of the positional arguments is a child node."
    return reduce(
      lambda l,r: l and r,
      map(
        lambda node: getattr(node, self.parent_id_field.name) is not None,
        args))

  def any_leaf_nodes(self, *args):
    "Return `True` if any of the positional arguments are leaf nodes."
    return reduce(
      lambda l,r: l or r,
      map(
        lambda node: getattr(node, self.left_field.name) ==
                     getattr(node, self.right_field.name)-1,
        args))

  def all_leaf_nodes(self, *args):
    """Return `False` unless every one of the positional arguments is a leaf
    node."""
    return reduce(
      lambda l,r: l and r,
      map(
        lambda node: getattr(node, self.left_field.name) ==
                     getattr(node, self.right_field.name)-1,
        args))

  def any_ancestors_of(self, descendant, *args, **kwargs):
    """Return `True` if the first positional argument is a descendant of any
    of the positional arguments that follow."""
    include_self = kwargs.pop('include_self', False) # Include self in results
    for extra in kwargs:
      raise TypeError, u"unexpected keyword argument '%s'" % extra
    return self._are_ancestors_of_helper(True, include_self, descendant, *args)

  def all_ancestors_of(self, descendant, *args, **kwargs):
    """Return `False` unless every one of the remaining positional arguments
    is a ancestor of the first."""
    include_self = kwargs.pop('include_self', False) # Include self in results
    for extra in kwargs:
      raise TypeError, u"unexpected keyword argument '%s'" % extra
    return self._are_ancestors_of_helper(False, include_self, descendant, *args)

  def _are_ancestors_of_helper(self, disjoint, include_self, descendant, *args):
    tree_id = getattr(descendant, self.tree_id_field.name)
    left    = getattr(descendant, self.left_field.name)
    right   = getattr(descendant, self.right_field.name)

    if include_self:
      left, right = left+1, right-1

    results = map(
      lambda node:getattr(node, self.tree_id_field.name) == tree_id and
                  getattr(node, self.left_field.name)    <  left    and
                  getattr(node, self.right_field.name)   >  right,
      args)

    if disjoint:
      return reduce(lambda l,r: l or r, results)
    else:
      return reduce(lambda l,r: l and r, results)

  def any_siblings_of(self, sibling, *args, **kwargs):
    """Return `True` if the first positional argument is a sibling of any of
    the positional arguments that follow."""
    include_self = kwargs.pop('include_self', False) # Include self in results
    for extra in kwargs:
      raise TypeError, u"unexpected keyword argument '%s'" % extra
    return self._are_siblings_of_helper(True, include_self, sibling, *args)

  def all_siblings_of(self, sibling, *args, **kwargs):
    """Return `False` unless every one of the remaining positional arguments
    is a sibling of the first."""
    include_self = kwargs.pop('include_self', False) # Include self in results
    for extra in kwargs:
      raise TypeError, u"unexpected keyword argument '%s'" % extra
    return self._are_siblings_of_helper(False, include_self, sibling, *args)

  def _are_siblings_of_helper(self, disjoint, include_self, sibling, *args):
    pk        = getattr(sibling, self.pk_field.name)
    parent_id = getattr(sibling, self.parent_id_field.name)

    if include_self:
      results = map(
        lambda node:getattr(node, self.parent_id_field.name) == parent_id and
                    getattr(node, self.pk_field.name)        != pk,
        args)
    else:
      results = map(
        lambda node:getattr(node, self.parent_id_field.name) == parent_id,
        args)

    if disjoint:
      return reduce(lambda l,r: l or r, results)
    else:
      return reduce(lambda l,r: l and r, results)

  def any_children_of(self, parent, *args):
    """Return `True` if the first positional argument is the parent of any of
    the positional arguments that follow."""
    return self._are_children_of_helper(True, parent, *args)

  def all_children_of(self, parent, *args):
    """Return `False` unless every one of the remaining positional arguments
    is a child of the first."""
    return self._are_children_of_helper(False, parent, *args)

  def _are_children_of_helper(self, disjoint, parent, *args):
    pk = getattr(parent, self.pk_field.name)

    results = map(
      lambda node:getattr(node, self.parent_id_field.name) == pk,
      args)

    if disjoint:
      return reduce(lambda l,r: l or r, results)
    else:
      return reduce(lambda l,r: l and r, results)

  def any_descendants_of(self, ancestor, *args, **kwargs):
    """Return `True` if the first positional argument is a ancestor of any of
    the positional arguments that follow."""
    include_self = kwargs.pop('include_self', False) # Include self in results
    for extra in kwargs:
      raise TypeError, u"unexpected keyword argument '%s'" % extra
    return self._are_descendants_of_helper(True, include_self, ancestor, *args)

  def all_descendants_of(self, ancestor, *args, **kwargs):
    """Return `False` unless every one of the remaining positional arguments
    is a descendant of the first."""
    include_self = kwargs.pop('include_self', False) # Include self in results
    for extra in kwargs:
      raise TypeError, u"unexpected keyword argument '%s'" % extra
    return self._are_descendants_of_helper(False, include_self, ancestor, *args)

  def _are_descendants_of_helper(self, disjoint, include_self, ancestor, *args):
    tree_id = getattr(ancestor, self.tree_id_field.name)
    left    = getattr(ancestor, self.left_field.name)
    right   = getattr(ancestor, self.right_field.name)

    if include_self:
      left = left-1

    results = map(
      lambda node:getattr(node, self.tree_id_field.name) == tree_id and
                  getattr(node, self.left_field.name)    >  left    and
                  getattr(node, self.left_field.name)    <  right,
      args)

    if disjoint:
      return reduce(lambda l,r: l or r, results)
    else:
      return reduce(lambda l,r: l and r, results)

  # Constants used to specify a desired position relative to another node, for
  # use in moving and insertion methods that take a target parameter.
  POSITION_LEFT        = 'left'
  POSITION_RIGHT       = 'right'
  POSITION_FIRST_CHILD = 'first-child'
  POSITION_LAST_CHILD  = 'last-child'

  def insert(self, node, target=None, position=POSITION_LAST_CHILD, session=None):
    ""
    options = self._tree_options

    setattr(node, options.delayed_op_attr, (target, position))

    setattr(node, options.tree_id_field.name, 0)

  def _get_session_from_args_or_self(self, *args):
    # Try retrieving the session from one of our positional parameters:
    for node in args:
      session = sqlalchemy.orm.object_session(node)
      if session is not None:
        return session
    # NOTE: ``self._get_obj`` only exists on instance managers--this
    #       fallback only works from an instance manager of a node
    #       associated with a session.
    return sqlalchemy.orm.object_session(self._get_obj())

# FIXME: write a helper routine that converts the args parameters of the
#   various *_of_node methods into standard form, so that either a positional
#   list of nodes, or a single list, set, or query object (or filter?) of
#   nodes in the first positional parameter can be used.

# ===----------------------------------------------------------------------===
# End of File
# ===----------------------------------------------------------------------===
