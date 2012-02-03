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

  def filter_root_nodes(self):
    "Get a filter condition for all root nodes."
    options = self._tree_options
    # We avoid using the adjacency-list parent field because that column may
    # or may not be indexed. The ``left`` field is always 1 on a root node,
    # and we know an index exists on that field.
    return options.left_field == 1

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
    options = self._tree_options
    return self.filter_root_nodes() & \
           options.tree_id_field.in_(args)

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
    options = self._tree_options
    return self.filter_root_nodes() & \
           options.tree_id_field.in_(
             map(lambda n:getattr(n, options.tree_id_field.name), args))

  def query_root_node_of_node(self, *args, **kwargs):
    """Returns the root nodes of the trees which contain the passed in nodes,
    using ``filter_root_node_by_tree_id``. The session used to perform the
    query is either a) the session explicitly passed in, b) the session
    associated with the first bound positional parameter, or c) the session
    associated with the instance manager's node."""
    session = kwargs.pop('session', None)
    if session is None:
      # Try retrieving the session from one of our positional parameters:
      for node in args:
        session = sqlalchemy.orm.object_session(node)
        if session is not None:
          break
      # NOTE: ``self._get_obj`` only exists on instance managers--session may
      #       only be ``None`` if called from an instance manager of a node
      #       associated with a session.
      if session is None:
        session
      session = sqlalchemy.orm.object_session(self._get_obj())
    return session.query(self.node_class) \
                  .filter(self.filter_root_node_of_node(*args, **kwargs))

  # Constants used to specify a desired position relative to another node, for
  # use in moving and insertion methods that take a target parameter.
  POSITION_LEFT        = 'left'
  POSITION_RIGHT       = 'right'
  POSITION_FIRST_CHILD = 'first-child'
  POSITION_LAST_CHILD  = 'last-child'

  def insert_node(self, node, target=None, position=POSITION_LAST_CHILD, session=None):
    """Sets up the tree state (``tree_id``, ``left``, ``right`` and ``depth``)
    for ``node`` (which has not yet been inserted into in the database) so it
    will be positioned relative to a given ``target`` node in the manner
    specified by ``position``, with any necessary space already having been
    made for it.

    A ``target`` of ``None`` indicates that ``node`` should become the last
    root node, which is a constant-time insertion operation. (Positioning root
    nodes with respect to other root nodes can be accomplished by using the
    ``POSITION_LEFT`` or ``POSITION_RIGHT`` constants and specifying the
    neighboring root node as ``target``)

    Accepted values for ``position`` are ``POSITION_FIRST_CHILD``,
    ``POSITION_LAST_CHILD``, ``POSITION_LEFT`` or ``POSITION_RIGHT``.
    ``POSITION_LAST_CHILD`` is likely to cause the least number of row
    updates, so therefore it is the default behavior if ``position`` is not
    specified.

    .. note::
      This is a low-level method; and naturally does NOT respect
      ``TreeOptions.order_insertion_by``. In most cases you should just set
      the node's parent and let this library call handle the details of
      insertion during the database flush.
    """
    options = self._tree_options

    # We need a session object in order to make changes to the database. We
    # give preference ot the session object associated with target over the
    # one associated with node (if they're different), since node might not be
    # associated with a session yet.
    if session is None:
      if target is not None:
        session = sqlalchemy.orm.object_session(target)
      else:
        session = sqlalchemy.orm.object_session(node)

    # Basic sanity check--this code is for inserting new nodes, not moving
    # existing nodes around.
    pk = getattr(node, options.pk_field.name)
    if pk is not None and session.query(self.node_class) \
                                 .filter(options.pk_field==pk).limit(1).count():
      raise ValueError(
        _(u"cannot insert a node which has already been saved; use " \
          u"move_node() instead"))

    if target is None:
      # Easy: no target is specified, so place it as the root node of a new
      # tree. This requires just one query (to find the id of the new tree)
      # and no row updates.
      setattr(node, options.parent_id_field.name, None)
      setattr(node, options.tree_id_field.name,   self._get_next_tree_id(session))
      setattr(node, options.left_field.name,      1)
      setattr(node, options.right_field.name,     2)
      setattr(node, options.depth_field.name,     0)

    elif getattr(target, options.parent_id_field.name) is None and \
         position in [self.POSITION_LEFT, self.POSITION_RIGHT]:
      # Almost as easy as the last case: the node will become a root node, so
      # we need only shift up by one the id value of any trees we are
      # displacing.
      target_tree_id = getattr(target, options.tree_id_field.name)
      if position == self.POSITION_LEFT:
        node_tree_id   = target_tree_id
        target_tree_id = target_tree_id - 1
      else:
        node_tree_id   = target_tree_id + 1
      self._manage_tree_gap(1, target_tree_id, session)

      setattr(node, options.parent_id_field.name, None)
      setattr(node, options.tree_id_field.name,   node_tree_id)
      setattr(node, options.left_field.name,      1)
      setattr(node, options.right_field.name,     2)
      setattr(node, options.depth_field.name,     0)

    else:
      # Otherwise our business is only slightly more messy. We need to
      # allocate space in the tree structure for our new node by shifting all
      # nodes to the right up by two spaces.
      setattr(node, options.left_field.name,  0)
      setattr(node, options.right_field.name, 1)
      setattr(node, options.depth_field.name, 0)

      gap_target, depth, left, parent, right_shift = \
        self._calculate_inter_tree_move_values(node, target, position, session)
      if parent is None:
        parent_id = None
        tree_id   = None
      else:
        parent_id = getattr(parent, options.pk_field.name)
        tree_id   = getattr(parent, options.tree_id_field.name)

      self._create_gap(right_shift, gap_target, tree_id, session)

      setattr(node, options.left_field.name,      left)
      setattr(node, options.right_field.name,     left + 1)
      setattr(node, options.depth_field.name,     depth)
      setattr(node, options.tree_id_field.name,   tree_id)
      setattr(node, options.parent_id_field.name, parent_id)

  def _get_next_tree_id(self, session):
    """Determines the next largest unused tree id for the tree managed by this
    manager."""
    options = self._tree_options

    return session.query((
      sqlalchemy.func.max(options.tree_id_field) + 1).label('tree_id')) \
      .all()[0][0] or 1

  def _manage_tree_gap(self, size, target_tree_id, session):
    """Creates space for a new tree *after* the target by incrementing all
    tree id's greater than ``target_tree_id``."""
    options = self._tree_options

    expr = options.table.update() \
      .values({options.tree_id_field.name: options.tree_id_field + size}) \
      .where(options.tree_id_field > target_tree_id)

    session.execute(expr)

  def _manage_space(self, size, target, tree_id, session):
    """Manages spaces in the tree identified by ``tree_id`` by changing the
    values of the left and right columns by ``size`` after the given
    ``target`` point."""
    options = self._tree_options

    expr = options.table.update() \
      .values({
        options.left_field:  sqlalchemy.case(
          [(options.left_field > target, options.left_field + size)],
          else_ = options.left_field),
        options.right_field: sqlalchemy.case(
          [(options.right_field > target, options.right_field + size)],
          else_ = options.right_field),
      }) \
      .where(
        (options.tree_id_field == tree_id) &
        ((options.left_field  > target) |
         (options.right_field > target))
      )

    session.execute(expr)

  def _create_gap(self, size, target, tree_id, session):
    """Creates a space of a certain ``size`` after the given ``target`` point
    in the tree identified by ``tree_id``."""
    self._manage_space(size, target, tree_id, session)

  def _close_gap(self, size, target, tree_id, session):
    """Closes a gap of a certain ``size`` after the given ``target`` point in
    the tree identified by ``tree_id``."""
    self._manage_space(-size, target, tree_id, session)

  def _calculate_inter_tree_move_values(self, node, target, position, session):
    """Calculates values required when moving ``node`` relative to ``target``
    as specified by ``position`` (one of ``left``, ``right``, ``first-child``
    or ``last-child``)."""
    options = self._tree_options

    node_left    = getattr(node,   options.left_field.name)
    node_right   = getattr(node,   options.right_field.name)
    node_depth   = getattr(node,   options.depth_field.name)
    target_left  = getattr(target, options.left_field.name)
    target_right = getattr(target, options.right_field.name)
    target_depth = getattr(target, options.depth_field.name)

    if position == self.POSITION_LAST_CHILD or position == self.POSITION_FIRST_CHILD:
      if position == self.POSITION_LAST_CHILD:
        gap_target = target_right - 1
      else:
        gap_target = target_left
      depth_change = target_depth - node_depth + 1
      parent = target

    elif position == self.POSITION_LEFT or position == self.POSITION_RIGHT:
      if position == self.POSITION_LEFT:
        gap_target = target_left - 1
      else:
        gap_target = target_right
      depth_change = target_depth - node_depth
      parent = getattr(target, options.parent_id_field.name)
      if parent:
        parent = session.query(self.node_class).filter(options.pk_field==parent).one()

    else:
      raise ValueError(_(u"an invalid position was given: %s") % position)

    left_right_change = gap_target - node_left + 1

    right_shift = 0
    if parent:
      right_shift = node_right - node_left + 1

    return gap_target, depth_change, left_right_change, parent, right_shift

# ===----------------------------------------------------------------------===
# End of File
# ===----------------------------------------------------------------------===
