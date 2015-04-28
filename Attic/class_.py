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
  def __init__(self, node_class, options):
    # Save our parameters for future use:
    self._tree_options = options
    self._node_class = node_class

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
    return session.query(self._node_class) \
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
    return session.query(self._node_class) \
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
    return session.query(self._node_class) \
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
    if pk is not None and session.query(self._node_class) \
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
        parent = session.query(self._node_class).filter(options.pk_field==parent).one()

    else:
      raise ValueError(_(u"an invalid position was given: %s") % position)

    left_right_change = gap_target - node_left + 1

    right_shift = 0
    if parent:
      right_shift = node_right - node_left + 1

    return gap_target, depth_change, left_right_change, parent, right_shift

  def move_node(self, node, target, position=POSITION_LAST_CHILD, session=None):
    """Moves ``node`` relative to a given ``target`` node as specified by
    ``position`` (when appropriate), by examining both nodes and calling the
    appropriate method to perform the move.

    A ``target`` of ``None`` indicates that ``node`` should be turned into a
    root node.

    Valid values for ``position`` are ``POSITION_LEFT``, ``POSITION_RIGHT``,
    ``POSITION_FIRST_CHILD`` or ``POSITION_LAST_CHILD``.

    ``node`` will be modified to reflect its new tree state in the database.
    Depending on the type of the move, a good many other nodes might be
    modified as well.

    This method explicitly checks for ``node`` being made a sibling of a root
    node, as this is a special case due to our use of tree ids to order root
    nodes.

    .. note::
      This is a low-level method; it does NOT respect
      ``MPTTMeta.order_insertion_by``. In most cases you should just move the
      node yourself by setting node.parent.
    """
    if session is None:
      session = sqlalchemy.orm.object_session(node)

    """
    if target is None:
      if node.is_child_node():
          self._make_child_root_node(node)
    elif target.is_root_node() and \
         position in [self.POSITION_LEFT, self.POSITION_RIGHT]:
      self._make_sibling_of_root_node(node, target, position)
    else:
      if node.is_root_node():
        self._move_root_node(node, target, position)
      else:
        self._move_child_node(node, target, position)
    """

  #def rebuild_all_trees(self, order_by=None):
  #  """Perform a complete rebuild of all trees on the basis of adjacency relations.
  #
  #  Drops indexes before processing and recreates it after.
  #
  #  :param order_by:
  #    an "order by clause" for sorting root nodes and a children nodes in each subtree.
  #  """
  #  options = self._tree_options
  #  order_by = order_by or options.pk_field
  #  for index in options.indices:
  #    index.drop()
  #  roots = sqlalchemy.select(
  #    [options.pk_field], options.parent_id_field == None
  #  ).order_by(order_by)
  #  update_query = options.table.update()
  #  for tree_id, root_node in enumerate(roots.execute().fetchall()):
  #    [node_id] = root_node
  #    # resetting path, depth and tree_id for root node:
  #    update_query.where(options.pk_field == node_id) \
  #                .values({options.tree_id_field: tree_id + 1,
  #                         options.path_field: '',
  #                         options.depth_field: 0}) \
  #                .execute()
  #    self._do_rebuild_subtree(node_id, '', 0, tree_id + 1, order_by)
  #  for index in options.indices:
  #    index.create()
  #  """
  #  if self._base_manager:
  #    return self._base_manager.rebuild()
  #
  #  opts = self.model._mptt_meta
  #
  #  qs = self._mptt_filter(parent__isnull=True)
  #  if opts.order_insertion_by:
  #    qs = qs.order_by(*opts.order_insertion_by)
  #  pks = qs.values_list('pk', flat=True)
  #
  #  idx = 0
  #  for pk in pks:
  #    idx += 1
  #    self._rebuild_helper(pk, 1, idx)
  #  """

  def _inter_tree_move_and_close_gap(self, node, depth_change,
          left_right_change, new_tree_id, parent_pk=None):
    """Removes ``node`` from its current tree, with the given set of changes
    being applied to ``node`` and its descendants, closing the gap left by
    moving ``node`` as it does so.

    If ``parent_pk`` is ``None``, this indicates that ``node`` is being moved
    to a brand new tree as its root node, and will thus have its parent field
    set to ``NULL``. Otherwise, ``node`` will have ``parent_pk`` set for its
    parent field."""
    options = self._tree_options

    inter_tree_move_query = """
    UPDATE %(table)s
    SET %(level)s = CASE
        WHEN %(left)s >= %%s AND %(left)s <= %%s
          THEN %(level)s - %%s
        ELSE %(level)s END,
      %(tree_id)s = CASE
        WHEN %(left)s >= %%s AND %(left)s <= %%s
          THEN %%s
        ELSE %(tree_id)s END,
      %(left)s = CASE
        WHEN %(left)s >= %%s AND %(left)s <= %%s
          THEN %(left)s - %%s
        WHEN %(left)s > %%s
          THEN %(left)s - %%s
        ELSE %(left)s END,
      %(right)s = CASE
        WHEN %(right)s >= %%s AND %(right)s <= %%s
          THEN %(right)s - %%s
        WHEN %(right)s > %%s
          THEN %(right)s - %%s
        ELSE %(right)s END,
      %(parent)s = CASE
        WHEN %(pk)s = %%s
          THEN %(new_parent)s
        ELSE %(parent)s END
    WHERE %(tree_id)s = %%s""" % {
      'table':      qn(self.tree_model._meta.db_table),
      'level':      qn(opts.get_field(options.depth_field.name  ).column),
      'left':       qn(opts.get_field(options.left_field.name   ).column),
      'tree_id':    qn(opts.get_field(options.tree_id_field.name).column),
      'right':      qn(opts.get_field(options.right_field.name  ).column),
      'parent':     qn(opts.get_field(options.parent_id_field.name ).column),
      'pk':         qn(opts.pk.column),
      'new_parent': parent_pk is None and 'NULL' or '%s',
    }

    left  = getattr(node, options.left_field.name)
    right = getattr(node, options.right_field.name)
    gap_size = right - left + 1
    gap_target_left  = left - 1
    params = [
      left, right, depth_change,
      left, right, new_tree_id,
      left, right, left_right_change,
      gap_target_left, gap_size,
      left, right, left_right_change,
      gap_target_left, gap_size,
      node.pk,
      getattr(node, options.tree_id_field.name)
    ]
    if parent_pk is not None:
      params.insert(-1, parent_pk)

    cursor = self._get_connection(node).cursor()

    cursor.execute(inter_tree_move_query, params)

  def _make_child_root_node(self, node, new_tree_id=None):
    """Removes ``node`` from its tree, making it the root node of a new tree.
    If ``new_tree_id`` is not specified a new tree id will be generated.
    ``node`` will be modified to reflect its new tree state in the
    database."""
    options = self._tree_options

    left  = getattr(node, options.left_field.name)
    right = getattr(node, options.right_field.name)
    depth = getattr(node, options.depth_field.name)
    if not new_tree_id:
      new_tree_id = self._get_next_tree_id()
    left_right_change = left - 1

    self._inter_tree_move_and_close_gap(node, level, left_right_change,
                                        new_tree_id)

    # Update the node to be consistent with the updated tree in the database:
    setattr(node, options.left_field.name,    left  - left_right_change)
    setattr(node, options.right_field.name,   right - left_right_change)
    setattr(node, options.depth_field.name,   0)
    setattr(node, options.tree_id_field.name, new_tree_id)
    setattr(node, options.parent_id_field.name,  None)
    node._mptt_cached_fields[options.parent_id_field.name] = None

  def _make_sibling_of_root_node(self, node, target, position):
    """Moves ``node``, making it a sibling of the given ``target`` root node
    as specified by ``position``.

    ``node`` will be modified to reflect its new tree state in the database.

    Since we use tree ids to reduce the number of rows affected by tree
    management during insertion and deletion, root nodes are not true
    siblings; thus, making an item a sibling of a root node is a special case
    which involves shuffling tree ids around."""
    if node == target:
      raise InvalidMoveError(_('A node may not be made a sibling of itself.'))

    opts           = self.model._meta
    tree_id        = getattr(node,   options.tree_id_field.name)
    target_tree_id = getattr(target, options.tree_id_field.name)

    if node.is_child_node():
      if position == self.POSITION_LEFT:
        gap_target = target_tree_id - 1
        new_tree_id  = target_tree_id
      elif position == self.POSITION_RIGHT:
        gap_target = target_tree_id
        new_tree_id  = target_tree_id + 1
      else:
        raise ValueError(_('An invalid position was given: %s.') % position)

      self._manage_tree_gap(1, gap_target, session)
      if tree_id > gap_target:
        # The node's tree id has been incremented in the database -- this
        # change must be reflected in the node object for the method call
        # below to operate on the correct tree.
        setattr(node, options.tree_id_field.name, tree_id + 1)
      self._make_child_root_node(node, new_tree_id)
    else:
      if position == self.POSITION_LEFT:
        if target_tree_id > tree_id:
          left_sibling = target.get_previous_sibling()
          if node == left_sibling:
            return
          new_tree_id = getattr(left_sibling, options.tree_id_field.name)
          lower_bound, upper_bound = tree_id, new_tree_id
          shift = -1
        else:
          new_tree_id = target_tree_id
          lower_bound, upper_bound = new_tree_id, tree_id
          shift = 1
      elif position == self.POSITION_RIGHT:
        if target_tree_id > tree_id:
          new_tree_id = target_tree_id
          lower_bound, upper_bound = tree_id, target_tree_id
          shift = -1
        else:
          right_sibling = target.get_next_sibling()
          if node == right_sibling:
            return
          new_tree_id = getattr(right_sibling, options.tree_id_field.name)
          lower_bound, upper_bound = new_tree_id, tree_id
          shift = 1
      else:
        raise ValueError(_('An invalid position was given: %s.') % position)

      root_sibling_query = """
      UPDATE %(table)s
      SET %(tree_id)s = CASE
            WHEN %(tree_id)s = %%s
              THEN %%s
            ELSE %(tree_id)s + %%s END
      WHERE %(tree_id)s >= %%s AND %(tree_id)s <= %%s""" % {
        'table':   qn(self.tree_model._meta.db_table),
        'tree_id': qn(opts.get_field(options.tree_id_field.name).column),
      }

      cursor = self._get_connection(node).cursor()
      cursor.execute(root_sibling_query, [tree_id, new_tree_id, shift,
                                          lower_bound, upper_bound])
      setattr(node, options.tree_id_field.name, new_tree_id)

  def _move_child_node(self, node, target, position):
    """Calls the appropriate method to move child node ``node`` relative to
    the given ``target`` node as specified by ``position``."""
    tree_id = getattr(node, options.tree_id_field.name)
    target_tree_id = getattr(target, options.tree_id_field.name)

    if tree_id == target_tree_id:
      self._move_child_within_tree(node, target, position)
    else:
      self._move_child_to_new_tree(node, target, position)

  def _move_child_to_new_tree(self, node, target, position):
    """Moves child node ``node`` to a different tree, inserting it relative to
    the given ``target`` node in the new tree as specified by ``position``.

    ``node`` will be modified to reflect its new tree state in the database.
    """
    left        = getattr(node,   options.left_field.name)
    right       = getattr(node,   options.right_field.name)
    depth       = getattr(node,   options.depth_field.name)
    new_tree_id = getattr(target, options.tree_id_field.name)

    gap_target, depth_change, left_right_change, parent, new_parent_right = \
      self._calculate_inter_tree_move_values(node, target, position, session)

    tree_width = right - left + 1

    # Make space for the subtree which will be moved
    self._create_gap(tree_width, gap_target, new_tree_id, session)
    # Move the subtree
    self._inter_tree_move_and_close_gap(node, depth_change,
      left_right_change, new_tree_id, parent.pk)

    # Update the node to be consistent with the updated
    # tree in the database.
    setattr(node, options.left_field.name,    left  - left_right_change)
    setattr(node, options.right_field.name,   right - left_right_change)
    setattr(node, options.depth_field.name,   depth - depth_change)
    setattr(node, options.tree_id_field.name, new_tree_id)
    setattr(node, options.parent_id_field.name,  parent)

    node._mptt_cached_fields[options.parent_id_field.name] = parent.pk

  def _move_child_within_tree(self, node, target, position):
    """Moves child node ``node`` within its current tree relative to the given
    ``target`` node as specified by ``position``.

    ``node`` will be modified to reflect its new tree state in the database.
    """
    left         = getattr(node, options.left_field.name)
    right        = getattr(node, options.right_field.name)
    depth        = getattr(node, options.depth_field.name)
    width        = right - left + 1
    tree_id      = getattr(node,   options.tree_id_field.name)
    target_left  = getattr(target, options.left_field.name)
    target_right = getattr(target, options.right_field.name)
    target_depth = getattr(target, options.depth_field.name)

    if position == self.POSITION_LAST_CHILD or position == self.POSITION_RIGHT:
      if node == target:
        raise InvalidMoveError(_('A node may not be made a child of itself.'))
      elif left < target_left < right:
        raise InvalidMoveError(_('A node may not be made a child of any of its descendants.'))
      if position == self.POSITION_LAST_CHILD:
        if target_right > right:
          new_left = target_right - width
          new_right = target_right - 1
        else:
          new_left = target_right
          new_right = target_right + width - 1
      else:
        if target_left > left:
          new_left = target_left - width + 1
          new_right = target_left
        else:
          new_left = target_left + 1
          new_right = target_left + width
      depth_change = depth - target_depth - 1
      parent = target
    elif position == self.POSITION_LEFT or position == self.POSITION_RIGHT:
      if node == target:
        raise InvalidMove(_('A node may not be made a sibling of itself.'))
      elif left < target_left < right:
        raise InvalidMove(_('A node may not be made a sibling of any of its descendants.'))
      if position == self.POSITION_LEFT:
        if target_left > left:
          new_left = target_left - width
          new_right = target_left - 1
        else:
          new_left = target_left
          new_right = target_left + width - 1
      else:
        if target_right > right:
          new_left = target_right - width + 1
          new_right = target_right
        else:
          new_left = target_right + 1
          new_right = target_right + width
      depth_change = depth - target_depth
      parent = getattr(target, options.parent_id_field.name)
    else:
      raise ValueError(_('An invalid position was given: %s.') % position)

    left_boundary     = min(left,  new_left)
    right_boundary    = max(right, new_right)
    left_right_change = new_left - left
    gap_size          = width
    if left_right_change > 0:
      gap_size = -gap_size

    opts = self.model._meta
    # The depth update must come before the left update to keep MySQL happy --
    # left seems to refer to the updated value immediately after its update
    # has been specified in the query with MySQL, but not with SQLite or
    # Postgres.
    move_subtree_query = """
    UPDATE %(table)s
    SET %(level)s = CASE
          WHEN %(left)s >= %%s AND %(left)s <= %%s
            THEN %(level)s - %%s
          ELSE %(level)s END,
        %(left)s = CASE
          WHEN %(left)s >= %%s AND %(left)s <= %%s
            THEN %(left)s + %%s
          WHEN %(left)s >= %%s AND %(left)s <= %%s
            THEN %(left)s + %%s
          ELSE %(left)s END,
        %(right)s = CASE
          WHEN %(right)s >= %%s AND %(right)s <= %%s
            THEN %(right)s + %%s
          WHEN %(right)s >= %%s AND %(right)s <= %%s
            THEN %(right)s + %%s
          ELSE %(right)s END,
        %(parent)s = CASE
          WHEN %(pk)s = %%s
            THEN %%s
          ELSE %(parent)s END
    WHERE %(tree_id)s = %%s""" % {
      'table':   qn(self.tree_model._meta.db_table),
      'level':   qn(opts.get_field(options.depth_field.name ).column),
      'left':    qn(opts.get_field(options.left_field.name  ).column),
      'right':   qn(opts.get_field(options.right_field.name ).column),
      'parent':  qn(opts.get_field(options.parent_id_field.name).column),
      'pk':      qn(opts.pk.column),
      'tree_id': qn(opts.get_field(options.tree_id_field.name).column),
    }

    cursor = self._get_connection(node).cursor()
    cursor.execute(move_subtree_query, [
      left, right, depth_change,
      left, right, left_right_change,
      left_boundary, right_boundary, gap_size,
      left, right, left_right_change,
      left_boundary, right_boundary, gap_size,
      node.pk, parent.pk,
      tree_id])

    # Update the node to be consistent with the updated
    # tree in the database.
    setattr(node, options.left_field.name,   new_left)
    setattr(node, options.right_field.name,  new_right)
    setattr(node, options.depth_field.name,  depth - depth_change)
    setattr(node, options.parent_id_field.name, parent)
    node._mptt_cached_fields[options.parent_id_field.name] = parent.pk

  def _move_root_node(self, node, target, position):
    """Moves root node``node`` to a different tree, inserting it relative to the given ``target`` node as specified by ``position``.

    ``node`` will be modified to reflect its new tree state in the database.
    """
    left        = getattr(node,   options.left_field.name)
    right       = getattr(node,   options.right_field.name)
    depth       = getattr(node,   options.depth_field.name)
    tree_id     = getattr(node,   options.tree_id_field.name)
    new_tree_id = getattr(target, options.tree_id_field.name)
    width       = right - left + 1

    if node == target:
      raise InvalidMove(_('A node may not be made a child of itself.'))
    elif tree_id == new_tree_id:
      raise InvalidMove(_('A node may not be made a child of any of its descendants.'))

    gap_target, depth_change, left_right_change, parent, right_shift = \
      self._calculate_inter_tree_move_values(node, target, position, session)

    # Create space for the tree which will be inserted
    self._create_gap(width, gap_target, new_tree_id, session)

    # Move the root node, making it a child node
    opts = self.model._meta
    move_tree_query = """
    UPDATE %(table)s
    SET %(level)s   = %(level)s - %%s,
        %(left)s    = %(left)s  - %%s,
        %(right)s   = %(right)s - %%s,
        %(tree_id)s = %%s,
        %(parent)s = CASE
          WHEN %(pk)s = %%s
            THEN %%s
          ELSE %(parent)s END
    WHERE %(left)s >= %%s AND %(left)s <= %%s
      AND %(tree_id)s = %%s""" % {
      'table':   qn(self.tree_model._meta.db_table),
      'level':   qn(opts.get_field(options.depth_field.name  ).column),
      'left':    qn(opts.get_field(options.left_field.name   ).column),
      'right':   qn(opts.get_field(options.right_field.name  ).column),
      'tree_id': qn(opts.get_field(options.tree_id_field.name).column),
      'parent':  qn(opts.get_field(options.parent_id_field.name ).column),
      'pk':      qn(opts.pk.column),
    }

    cursor = self._get_connection(node).cursor()
    cursor.execute(move_tree_query, [depth_change, left_right_change,
      left_right_change, new_tree_id, node.pk, parent.pk, left, right,
      tree_id])

    # Update the former root node to be consistent with the updated
    # tree in the database.
    setattr(node, options.left_field.name,    left  - left_right_change)
    setattr(node, options.right_field.name,   right - left_right_change)
    setattr(node, options.depth_field.name,   depth - depth_change)
    setattr(node, options.tree_id_field.name, new_tree_id)
    setattr(node, options.parent_id_field.name,  parent)
    node._mptt_cached_fields[options.parent_id_field.name] = parent.pk

  def _do_rebuild_subtree(self, root_node_id, root_path, root_depth, \
                          tree_id, order_by):
    """The main recursive function for rebuilding trees.

    :param root_node_id:
      subtree's root node primary key value.
    :param root_path:
      the pre-calculated path of root node.
    :param root_depth:
      the pre-calculated root node's depth.
    :param tree_id:
      the pre-calculated identifier for this tree.
    :param order_by:
      the children sort order.
    """
    options = self._tree_options
    path = root_path + ALPHABET[0] * options.steplen
    depth = root_depth + 1
    children = sqlalchemy.select(
      [options.pk_field],
      options.parent_id_field == root_node_id
    ).order_by(order_by)
    query = options.table.update()
    for child in children.execute().fetchall():
      [child] = child
      query.where(options.pk_field == child) \
           .values({options.path_field: path, \
                    options.depth_field: depth, \
                    options.tree_id_field: tree_id}).execute()
      self._do_rebuild_subtree(child, path, depth, tree_id, order_by)
      path = inc_path(path, options.steplen)

  # FIXME: This is a very cunning query re-writing function for Django MPTT...
  #        can we adapt this to SQLAlchemy?
  #
  #def _translate_lookups(self, **lookups):
  #  new_lookups = {}
  #  for k, v in lookups.items():
  #    parts = k.split('__')
  #    new_parts = []
  #    for part in parts:
  #      new_parts.append(getattr(self, '%s_field' % part, part))
  #    new_lookups['__'.join(new_parts)] = v
  #  return new_lookups
  #
  #def _mptt_filter(self, qs=None, **filters):
  #  "Like self.filter(), but translates name-agnostic filters for MPTT fields."
  #  if self._base_manager:
  #    return self._base_manager._mptt_filter(qs=qs, **filters)
  #
  #  if qs is None:
  #    qs = self.get_query_set()
  #  return qs.filter(**self._translate_lookups(**filters))
  #
  #def _mptt_update(self, qs=None, **items):
  #  "Like self.update(), but translates name-agnostic MPTT fields."
  #  if self._base_manager:
  #    return self._base_manager._mptt_update(qs=qs, **items)
  #
  #  if qs is None:
  #    qs = self.get_query_set()
  #  return qs.update(**self._translate_lookups(**items))

  # FIXME: What follows is a method for annotating Django querysets with
  #        counts based on relationships with other models. I haven't followed
  #        exactly how this works, but at some point we should figure out what
  #        it does and decided how we can provide the same service in
  #        SQLAlchemy.
  #
  #COUNT_SUBQUERY = """(
  #  SELECT COUNT(*)
  #    FROM %(rel_table)s
  #   WHERE %(mptt_fk)s = %(mptt_table)s.%(mptt_pk)s
  #)"""
  #
  #CUMULATIVE_COUNT_SUBQUERY = """(
  #  SELECT COUNT(*)
  #    FROM %(rel_table)s
  #   WHERE %(mptt_fk)s IN
  #  (
  #    SELECT m2.%(mptt_pk)s
  #      FROM %(mptt_table)s m2
  #     WHERE m2.%(tree_id)s = %(mptt_table)s.%(tree_id)s
  #       AND m2.%(left)s BETWEEN %(mptt_table)s.%(left)s
  #                           AND %(mptt_table)s.%(right)s
  #  )
  #)"""
  #
  #def add_related_count(self, queryset, rel_model, rel_field, count_attr,
  #                      cumulative=False):
  #  """Adds a related item count to a given ``QuerySet`` using its ``extra``
  #  method, for a ``Model`` class which has a relation to this ``Manager``'s
  #  ``Model`` class.
  #
  #  Arguments:
  #
  #  ``rel_model``
  #    A ``Model`` class which has a relation to this `Manager``'s ``Model``
  #    class.
  #
  #  ``rel_field``
  #    The name of the field in ``rel_model`` which holds the relation.
  #
  #  ``count_attr``
  #    The name of an attribute which should be added to each item in this
  #    ``QuerySet``, containing a count of how many instances of ``rel_model``
  #    are related to it through ``rel_field``.
  #
  #  ``cumulative``
  #    If ``True``, the count will be for each item and all of its descendants,
  #    otherwise it will be for each item itself.
  #  """
  #  meta = self.model._meta
  #  if cumulative:
  #    subquery = CUMULATIVE_COUNT_SUBQUERY % {
  #      'rel_table':  qn(rel_model._meta.db_table),
  #      'mptt_fk':    qn(rel_model._meta.get_field(rel_field).column),
  #      'mptt_table': qn(self.tree_model._meta.db_table),
  #      'mptt_pk':    qn(meta.pk.column),
  #      'tree_id':    qn(meta.get_field(options.tree_id_field.name).column),
  #      'left':       qn(meta.get_field(options.left_field.name   ).column),
  #      'right':      qn(meta.get_field(options.right_field.name  ).column),
  #    }
  #  else:
  #    subquery = COUNT_SUBQUERY % {
  #      'rel_table':  qn(rel_model._meta.db_table),
  #      'mptt_fk':    qn(rel_model._meta.get_field(rel_field).column),
  #      'mptt_table': qn(self.tree_model._meta.db_table),
  #      'mptt_pk':    qn(meta.pk.column),
  #    }
  #  return queryset.extra(select={count_attr: subquery})

# ===----------------------------------------------------------------------===
# End of File
# ===----------------------------------------------------------------------===
