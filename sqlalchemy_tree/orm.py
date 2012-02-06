#!/usr/bin/env python
# -*- coding: utf-8 -*-

# === sqlalchemy_tree.orm -------------------------------------------------===
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

import sqlalchemy

__all__ = (
  'TreeMapperExtension',
  'TreeSessionExtension',
)

# ===----------------------------------------------------------------------===

class TreeMapperExtension(sqlalchemy.orm.interfaces.MapperExtension):
  """An extension to a node class' mapper, handling insertion, deletion, and
  updates of tree nodes. This class is instantiated by the manager object, and
  the average developer need not bother himself with it.

  :param options:
    instance of :class:`TreeOptions`
  """
  def __init__(self, options):
    super(TreeMapperExtension, self).__init__()
    # Save the options for future use.
    self._tree_options = options

  def _reload_tree_parameters(self, connection, *args):
    ""
    options = self._tree_options

    for node in args:
      if node is None:
        continue

      node_pk = getattr(node, options.pk_field.name)
      if node_pk is None:
        continue

      parent_id, tree_id, left, right, depth = connection.execute(
        sqlalchemy.select([
          options.parent_id_field,
          options.tree_id_field,
          options.left_field,
          options.right_field,
          options.depth_field,
        ])
        .where(options.pk_field==node_pk)
      ).fetchone()

      setattr(node, options.parent_id_field.name, parent_id)
      setattr(node, options.tree_id_field.name,   tree_id)
      setattr(node, options.left_field.name,      left)
      setattr(node, options.right_field.name,     right)
      setattr(node, options.depth_field.name,     depth)

  def before_insert(self, mapper, connection, node):
    """Just prior to a previously non-existent node being inserted into the
    tree.

    Sets up the tree state (``tree_id``, ``left``, ``right`` and ``depth``)
    for ``node`` (which has not yet been inserted into in the database) so it
    will be positioned relative to a given ``target`` node in the manner
    specified by ``position`` (the insertion parameters), with any necessary
    space already having been made for it.

    ``target`` and ``position`` are stored on a hidden attribute of node,
    having been set when ``TreeManager.insert`` was called by the user, or
    otherwise auto-generated by the session's ``before_flush`` handler.

    A ``target`` of ``None`` indicates that ``node`` should become the last
    root node, which is a constant-time insertion operation. (Positioning root
    nodes with respect to other root nodes can be accomplished by using the
    ``POSITION_LEFT`` or ``POSITION_RIGHT`` constants and specifying the
    neighboring root node as ``target``.)

    Accepted values for ``position`` are ``POSITION_FIRST_CHILD``,
    ``POSITION_LAST_CHILD``, ``POSITION_LEFT`` or ``POSITION_RIGHT``.
    ``POSITION_LAST_CHILD`` is likely to cause the least number of row
    updates, so therefore it is the default behavior if ``position`` is not
    specified.
    """
    options = self._tree_options

    target, position = getattr(node, options.delayed_op_attr)
    delattr(node, options.delayed_op_attr)

    self._reload_tree_parameters(connection, node, target)

    if target is None:
      # Easy: no target is specified, so place it as the root node of a new
      # tree. This requires just one query (to find the id of the new tree)
      # and no row updates.
      tree_id = self._get_next_tree_id(connection)
      setattr(node, options.parent_id_field.name, None)
      setattr(node, options.tree_id_field.name,   tree_id)
      setattr(node, options.left_field.name,      1)
      setattr(node, options.right_field.name,     2)
      setattr(node, options.depth_field.name,     0)

    elif (getattr(target, options.left_field.name)==1 and
          position in [options.class_manager.POSITION_LEFT,
                       options.class_manager.POSITION_RIGHT]):
      # Almost as easy as the last case: the node will become a root node, so
      # we need only shift up by one the id value of any trees we are
      # displacing.
      target_tree_id = getattr(target, options.tree_id_field.name)
      if position == options.class_manager.POSITION_LEFT:
        node_tree_id   = target_tree_id
        target_tree_id = target_tree_id - 1
      else:
        node_tree_id   = target_tree_id + 1
      self._manage_tree_gap(connection, target_tree_id, 1)

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

      gap_target, depth, left, parent_id, right_shift = \
        self._calculate_inter_tree_move_values(node, target, position)
      if parent_id is None:
        tree_id = None
      else:
        tree_id = connection.execute(
          sqlalchemy.select([
            options.tree_id_field,
          ])
          .where(options.pk_field == parent_id)
        ).fetchone()[0]

      self._manage_position_gap(connection, tree_id, gap_target, right_shift)

      setattr(node, options.parent_id_field.name, parent_id)
      setattr(node, options.left_field.name,      left)
      setattr(node, options.right_field.name,     left + 1)
      setattr(node, options.depth_field.name,     depth)
      setattr(node, options.tree_id_field.name,   tree_id)

  def after_insert(self, mapper, connection, node):
    "Just after a previously non-existent node is inserted into the tree."
    pass

  def before_delete(self, mapper, connection, node):
    "Just prior to an existent node being deleted."
    options = self._tree_options

    self._reload_tree_parameters(connection, node)

    # To prevent any cascade effects, we NULL-out any adjacency-list links to
    # the node being deleted. These links will be replaced with proper values
    # in the after_delete handler.
    connection.execute(
      sqlalchemy.update(options.table)
        .values({options.parent_id_field: None})
        .where(options.parent_id_field == getattr(node, options.pk_field.name))
    )

  def after_delete(self, mapper, connection, node):
    "Just after an existent node is updated."
    options = self._tree_options

    parent_id = getattr(node, options.parent_id_field.name)
    tree_id   = getattr(node, options.tree_id_field.name)
    left      = getattr(node, options.left_field.name)
    right     = getattr(node, options.right_field.name)
    depth     = getattr(node, options.depth_field.name)

    if left == 1:
      # Root node! Any children will be promoted to be root nodes themselves.

      # First we gather information about the immediate children:
      children = connection.execute(
        sqlalchemy.select([
          options.left_field,
          options.right_field])
        .where(
          (options.tree_id_field == tree_id) &
          (options.left_field     > left)    &
          (options.left_field     < right)   &
          (options.depth_field   == depth + 1))
        .order_by(
          sqlalchemy.asc(options.left_field))
      ).fetchall()

      # We either close the gap formed by removing the tree (if there are no
      # children), or make room for a separate tree for each child:
      self._manage_tree_gap(connection, tree_id, len(children)-1)

      # Now for each child we promote that child to be root node of a new
      # tree, updating all of it and its children's tree parameters:
      next_tree_id = tree_id
      for child_left, child_right in children:
        # The shift is how much the positional fields (left/right) will have
        # to be adjusted so that the new root node starts from 1.
        shift = child_left - 1
        # Assign the new tree parameters:
        connection.execute(options.table.update()
          .values({
            options.tree_id_field: next_tree_id,
            options.left_field:    options.left_field  - shift,
            options.right_field:   options.right_field - shift,
            options.depth_field:   options.depth_field - 1})
          .where(
            (options.tree_id_field == tree_id) &
            (options.left_field >= child_left) &
            (options.left_field <= child_right)))
        # Increment the tree_id for the next time through the loop:
        next_tree_id += 1

    else:
      # Child node, which is much simper than the root node case. We simply
      # update the tree parameters of the children and eliminate the two gaps
      # where the old node's left and right values were.
      connection.execute(options.table.update()
        .values({
          # if left > node.left and left < node.right and depth == node.depth + 1:
          #   parent = node.parent
          # else:
          #   parent = parent
          options.parent_id_field: sqlalchemy.case(
            [((options.left_field > left) & (options.left_field < right) & (options.depth_field == depth + 1), parent_id)],
            else_ = options.parent_id_field),
          # if left > node.left and left < node.right:
          #   left = left - 1
          # elif left > right:
          #   left = left - 2
          # else:
          #   left = left
          options.left_field:      sqlalchemy.case(
            [((options.left_field > left) & (options.left_field < right), options.left_field - 1),
             ((options.left_field > right),                               options.left_field - 2)],
            else_ =                                                       options.left_field),
          # if right > node.left and right < node.right:
          #   right = right - 1
          # elif right > right:
          #   right = right - 2
          # else:
          #   right = right
          options.right_field:     sqlalchemy.case(
            [((options.right_field > left) & (options.right_field < right), options.right_field - 1),
             ((options.right_field > right),                                options.right_field - 2)],
            else_ =                                                         options.right_field),
          # if left > node.left and left < node.right:
          #   depth = depth - 1
          # else:
          #   depth = depth
          options.depth_field:     sqlalchemy.case(
            [((options.left_field > left) & (options.left_field < right), options.depth_field - 1)],
            else_ = options.depth_field)})
        # Only update the tree the original node was a part of:
        .where((options.tree_id_field == tree_id)))

  def before_update(self, mapper, connection, node):
    """Called just prior to an existent node being updated.

    Possibly moves ``node`` relative to a given ``target`` node as specified
    by ``position`` (when appropriate), by examining both nodes and calling
    the appropriate method to perform the move.

    ``target`` and ``position`` are stored on a hidden attribute of node,
    having been set when ``TreeManager.insert`` was called by the user, or
    otherwise auto-generated by the session's ``before_flush`` handler upon
    detection of an adjacency-list change.

    A ``target`` of ``None`` indicates that ``node`` should be made into the
    last root node. (Positioning root nodes with respect to other root nodes
    can be accomplished by using the ``POSITION_LEFT`` or ``POSITION_RIGHT``
    constants and specifying the neighboring root node as ``target``.)

    Valid values for ``position`` are ``POSITION_LEFT``, ``POSITION_RIGHT``,
    ``POSITION_FIRST_CHILD`` or ``POSITION_LAST_CHILD``.

    ``node`` will be modified to reflect its new tree state in the database.
    Depending on the type of the move, a good many other nodes might be
    modified as well.

    This method explicitly checks for ``node`` being made a sibling of a root
    node, as this is a special case due to our use of tree ids to order root
    nodes.
    """
    options = self._tree_options

    if not hasattr(node, options.delayed_op_attr):
      return

    target, position = getattr(node, options.delayed_op_attr)
    delattr(node, options.delayed_op_attr)

    self._reload_tree_parameters(connection, node, target)

    node_is_root_node = getattr(node, options.left_field.name) == 1

    if target is None:
      if not node_is_root_node:
        self._make_child_into_root_node(connection, node)

    elif (getattr(target, options.left_field.name)==1 and
          position in [options.class_manager.POSITION_LEFT,
                       options.class_manager.POSITION_RIGHT]):
      self._make_sibling_of_root_node(connection, node, target, position)

    else:
      if node_is_root_node:
        self._move_root_node(connection, node, target, position)

      else:
        self._move_child_node(connection, node, target, position)

  def after_update(self, mapper, connection, node):
    "Just after an existent node is updated."
    pass

  def _get_next_tree_id(self, connection):
    """Determines the next largest unused tree id."""
    options = self._tree_options
    return connection.execute(
      sqlalchemy.select([
        (sqlalchemy.func.max(options.tree_id_field) + 1).label('tree_id')
      ])).fetchone()[0] or 1

  def _manage_tree_gap(self, connection, target_tree_id, size):
    """Creates space for a new tree *after* the target by adding ``size`` to
    all tree id's greater than ``target_tree_id``."""
    options = self._tree_options
    connection.execute(
      options.table.update()
        .values({options.tree_id_field: options.tree_id_field + size})
        .where(options.tree_id_field > target_tree_id))

  def _manage_position_gap(self, connection, tree_id, target, size):
    """Manages spaces in the tree identified by ``tree_id`` by changing the
    values of the left and right columns by ``size`` after the given
    ``target`` point."""
    options = self._tree_options
    connection.execute(
      options.table.update()
        .values({
          options.left_field:  sqlalchemy.case(
            [(options.left_field > target, options.left_field + size)],
            else_ = options.left_field),
          options.right_field: sqlalchemy.case(
            [(options.right_field > target, options.right_field + size)],
            else_ = options.right_field),
        })
        .where(
          (options.tree_id_field == tree_id) &
          ((options.left_field  > target) |
           (options.right_field > target))
        ))

  def _calculate_inter_tree_move_values(self, node, target, position):
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

    if (position == options.class_manager.POSITION_LAST_CHILD or
        position == options.class_manager.POSITION_FIRST_CHILD):
      if position == options.class_manager.POSITION_LAST_CHILD:
        gap_target = target_right - 1
      else:
        gap_target = target_left
      depth_change = target_depth - node_depth + 1
      parent_id = getattr(target, options.pk_field.name)

    elif (position == options.class_manager.POSITION_LEFT or
          position == options.class_manager.POSITION_RIGHT):
      if position == options.class_manager.POSITION_LEFT:
        gap_target = target_left - 1
      else:
        gap_target = target_right
      depth_change = target_depth - node_depth
      parent_id = getattr(target, options.parent_id_field.name)

    else:
      raise ValueError(_(u"an invalid position was given: %s") % position)

    left_right_change = gap_target - node_left + 1

    right_shift = 0
    if parent_id:
      right_shift = node_right - node_left + 1

    return gap_target, depth_change, left_right_change, parent_id, right_shift

  def _inter_tree_move_and_close_gap(self, connection, node, new_tree_id,
    left_right_change, depth_change, parent_id=None):
    """Removes ``node`` from its current tree, with the given set of changes
    being applied to ``node`` and its descendants, closing the gap left by
    moving ``node`` as it does so.

    If ``parent_id`` is ``None``, this indicates that ``node`` is being moved
    to a brand new tree as its root node, and will thus have its parent field
    set to ``NULL``. Otherwise, ``node`` will have ``parent_id`` set for its
    parent field."""
    options = self._tree_options

    left  = getattr(node, options.left_field.name)
    right = getattr(node, options.right_field.name)
    depth = getattr(node, options.depth_field.name)
    gap_size = right - left + 1

    connection.execute(
      options.table.update()
        .values({
          options.parent_id_field: sqlalchemy.case(
            [(options.pk_field == getattr(node, options.pk_field.name), parent_id)],
            else_ = options.parent_id_field),
          options.tree_id_field:   sqlalchemy.case(
            [((options.left_field >= left) & (options.left_field <= right), new_tree_id)],
            else_ = options.tree_id_field),
          options.left_field:      sqlalchemy.case(
            [((options.left_field >= left) & (options.left_field <= right), options.left_field + left_right_change),
             ((options.left_field >  right),                                options.left_field - gap_size)],
            else_ = options.left_field),
          options.right_field:     sqlalchemy.case(
            [((options.right_field >= left) & (options.right_field <= right), options.right_field + left_right_change),
             ((options.right_field >  right),                                 options.right_field - gap_size)],
            else_ = options.right_field),
          options.depth_field:     sqlalchemy.case(
            [((options.left_field >= left) & (options.left_field <= right), options.depth_field + depth_change)],
            else_ = options.depth_field),
        })
        .where(options.tree_id_field == getattr(node, options.tree_id_field.name)))

    setattr(node, options.parent_id_field.name, parent_id)
    setattr(node, options.tree_id_field.name,   new_tree_id)
    setattr(node, options.left_field.name,      left  + left_right_change)
    setattr(node, options.right_field.name,     right + left_right_change)
    setattr(node, options.depth_field.name,     depth + depth_change)

  def _make_child_into_root_node(self, connection, node, new_tree_id=None):
    """Removes ``node`` from its tree, making it the root node of a new tree.
    If ``new_tree_id`` is not specified a new tree id will be generated."""
    options = self._tree_options

    if not new_tree_id:
      new_tree_id = self._get_next_tree_id(connection)

    left  = getattr(node, options.left_field.name)
    right = getattr(node, options.right_field.name)
    depth = getattr(node, options.depth_field.name)
    left_right_change = 1 - left
    depth_change = -depth

    self._inter_tree_move_and_close_gap(connection, node, new_tree_id,
                                        left_right_change, depth_change)

  def _make_sibling_of_root_node(self, connection, node, target, position):
    """Moves ``node``, making it a sibling of the given ``target`` root node
    as specified by ``position``.

    Since we use tree ids to reduce the number of rows affected by tree
    management during insertion and deletion, root nodes are not true
    siblings; thus, making an item a sibling of a root node is a special case
    which involves shuffling tree ids around."""
    options = self._tree_options

    if node == target:
      raise InvalidMoveError(_(u"a node may not be made a sibling of itself"))

    tree_id        = getattr(node,   options.tree_id_field.name)
    target_tree_id = getattr(target, options.tree_id_field.name)

    if getattr(node, options.left_field.name) > 1:
      if position == options.class_manager.POSITION_LEFT:
        gap_target  = target_tree_id - 1
        new_tree_id = target_tree_id
      elif position == options.class_manager.POSITION_RIGHT:
        gap_target  = target_tree_id
        new_tree_id = target_tree_id + 1
      else:
        raise ValueError(_(u"an invalid position was given: %s") % position)

      self._manage_tree_gap(connection, gap_target, 1)

      if tree_id > gap_target:
        # The node's tree id has been incremented in the database -- this
        # change must be reflected in the node object for the method call
        # below to operate on the correct tree.
        setattr(node, options.tree_id_field.name, tree_id + 1)

      self._make_child_into_root_node(connection, node, new_tree_id)

    else:
      if position == options.class_manager.POSITION_LEFT:
        if target_tree_id > tree_id:
          new_tree_id = target_tree_id - 1
          if tree_id == new_tree_id:
            return
          lower_bound, upper_bound = tree_id, new_tree_id
          shift = -1
        else:
          new_tree_id = target_tree_id
          lower_bound, upper_bound = new_tree_id, tree_id
          shift = 1
      elif position == options.class_manager.POSITION_RIGHT:
        if target_tree_id > tree_id:
          new_tree_id = target_tree_id
          lower_bound, upper_bound = tree_id, target_tree_id
          shift = -1
        else:
          new_tree_id = target_tree_id + 1
          if node == new_tree_id:
            return
          lower_bound, upper_bound = new_tree_id, tree_id
          shift = 1
      else:
        raise ValueError(_(u"an invalid position was given: %s") % position)

      connection.execute(
        options.table.update()
          .values({
            options.tree_id_field: sqlalchemy.case(
              [(options.tree_id_field == tree_id, new_tree_id)],
              else_ = options.tree_id_field + shift),
          })
          .where(
            (options.tree_id_field >= lower_bound) &
            (options.tree_id_field <= upper_bound)
          ))

      setattr(node, options.tree_id_field.name, new_tree_id)

  def _move_root_node(self, connection, node, target, position):
    """Moves root node``node`` to a different tree, inserting it relative to
    the given ``target`` node as specified by ``position``."""
    options = self._tree_options

    tree_id     = getattr(node,   options.tree_id_field.name)
    left        = getattr(node,   options.left_field.name)
    right       = getattr(node,   options.right_field.name)
    depth       = getattr(node,   options.depth_field.name)
    new_tree_id = getattr(target, options.tree_id_field.name)

    if node == target:
      raise InvalidMove(_(u"a node may not be made a child of itself"))
    elif tree_id == new_tree_id:
      raise InvalidMove(_(u"a node may not be made a child of any of its descendants"))

    gap_target, depth_change, left_right_change, parent_id, right_shift = \
      self._calculate_inter_tree_move_values(node, target, position)

    # Create space for the tree which will be inserted
    self._manage_position_gap(connection, new_tree_id, gap_target, right_shift)

    # Move the root node, making it a child node
    connection.execute(
      options.table.update()
      .values({
        options.parent_id_field: sqlalchemy.case(
          [(options.pk_field == getattr(node, options.pk_field.name), parent_id)],
          else_ = options.parent_id_field),
        options.tree_id_field:   new_tree_id,
        options.left_field:      options.left_field  + left_right_change,
        options.right_field:     options.right_field + left_right_change,
        options.depth_field:     options.depth_field + depth_change,
      })
      .where(
        (options.tree_id_field == tree_id) &
        (options.left_field    >= left)    &
        (options.left_field    <= right)
      ))

    # Remove the gap previously occupied by the tree
    self._manage_tree_gap(connection, tree_id - 1, -1)

    # Closing the tree id gap might have affected the new tree id. We detect
    # this so we don't end up with an inconsistent structure later:
    if new_tree_id >= tree_id:
      new_tree_id -= 1

    # Update the former root node to be consistent with the updated
    # tree in the database.
    setattr(node, options.parent_id_field.name, parent_id)
    setattr(node, options.tree_id_field.name,   new_tree_id)
    setattr(node, options.left_field.name,      left  + left_right_change)
    setattr(node, options.right_field.name,     right + left_right_change)
    setattr(node, options.depth_field.name,     depth + depth_change)

  def _move_child_node(self, connection, node, target, position):
    """Calls the appropriate method to move child node ``node`` relative to
    the given ``target`` node as specified by ``position``."""
    options = self._tree_options

    tree_id     = getattr(node,   options.tree_id_field.name)
    new_tree_id = getattr(target, options.tree_id_field.name)

    if tree_id == new_tree_id:
      self._move_child_within_tree(connection, node, target, position)
    else:
      self._move_child_to_new_tree(connection, node, target, position)

  def _move_child_to_new_tree(self, connection, node, target, position):
    """Moves child node ``node`` to a different tree, inserting it relative to
    the given ``target`` node in the new tree as specified by ``position``."""
    options = self._tree_options

    left        = getattr(node,   options.left_field.name)
    right       = getattr(node,   options.right_field.name)
    depth       = getattr(node,   options.depth_field.name)
    new_tree_id = getattr(target, options.tree_id_field.name)
    width       = right - left + 1

    gap_target, depth_change, left_right_change, parent_id, right_shift = \
      self._calculate_inter_tree_move_values(node, target, position)

    # Make space for the subtree which will be moved
    self._manage_position_gap(connection, new_tree_id, gap_target, width)

    # Move the subtree
    self._inter_tree_move_and_close_gap(connection, node, new_tree_id,
      left_right_change, depth_change, parent_id)

  def _move_child_within_tree(self, connection, node, target, position):
    """Moves child node ``node`` within its current tree relative to the given
    ``target`` node as specified by ``position``."""
    options = self._tree_options

    left         = getattr(node,   options.left_field.name)
    right        = getattr(node,   options.right_field.name)
    depth        = getattr(node,   options.depth_field.name)
    width        = right - left + 1
    tree_id      = getattr(node,   options.tree_id_field.name)
    target_left  = getattr(target, options.left_field.name)
    target_right = getattr(target, options.right_field.name)
    target_depth = getattr(target, options.depth_field.name)

    if position in [options.class_manager.POSITION_FIRST_CHILD,
                    options.class_manager.POSITION_LAST_CHILD]:
      if node == target:
        raise InvalidMoveError(_(u"a node may not be made a child of itself"))
      elif left < target_left < right:
        raise InvalidMoveError(_(u"a node may not be made a child of any of its descendants"))

      if position == options.class_manager.POSITION_FIRST_CHILD:
        if target_left > left:
          new_left  = target_left - width + 1
          new_right = target_left
        else:
          new_left  = target_left + 1
          new_right = target_left + width
      else:
        if target_right > right:
          new_left  = target_right - width
          new_right = target_right - 1
        else:
          new_left  = target_right
          new_right = target_right + width - 1
      depth_change = target_depth - depth + 1
      parent_id = getattr(target, options.pk_field.name)

    elif position in [options.class_manager.POSITION_LEFT,
                      options.class_manager.POSITION_RIGHT]:
      if node == target:
        raise InvalidMove(_(u"a node may not be made a sibling of itself"))
      elif left < target_left < right:
        raise InvalidMove(_(u"a node may not be made a sibling of any of its descendants"))

      if position == options.class_manager.POSITION_LEFT:
        if target_left > left:
          new_left  = target_left - width
          new_right = target_left - 1
        else:
          new_left  = target_left
          new_right = target_left + width - 1
      else:
        if target_right > right:
          new_left  = target_right - width + 1
          new_right = target_right
        else:
          new_left  = target_right + 1
          new_right = target_right + width
      depth_change = target_depth - depth
      parent_id = getattr(target, options.parent_id_field.name)

    else:
      raise ValueError(_(u"an invalid position was given: %s") % position)

    left_boundary     = min(left,  new_left)
    right_boundary    = max(right, new_right)
    left_right_change = new_left - left
    gap_size          = width
    if left_right_change > 0:
      gap_size = -gap_size

    connection.execute(
      options.table.update()
      .values({
        options.depth_field:     sqlalchemy.case(
          [((options.left_field >= left) & (options.left_field <= right), options.depth_field + depth_change)],
          else_ = options.depth_field),
        options.left_field:      sqlalchemy.case(
          [((options.left_field >= left)          & (options.left_field <= right),          options.left_field + left_right_change),
           ((options.left_field >= left_boundary) & (options.left_field <= right_boundary), options.left_field + gap_size)],
          else_ = options.left_field),
        options.right_field:     sqlalchemy.case(
          [((options.right_field >= left)          & (options.right_field <= right),          options.right_field + left_right_change),
           ((options.right_field >= left_boundary) & (options.right_field <= right_boundary), options.right_field + gap_size)],
          else_ = options.right_field),
        options.parent_id_field: sqlalchemy.case(
          [(options.pk_field == getattr(node, options.pk_field.name), parent_id)],
          else_ = options.parent_id_field),
      })
      .where(options.tree_id_field == tree_id))

    # Update the node object to be consistent database.
    setattr(node, options.parent_id_field.name, parent_id)
    setattr(node, options.left_field.name,      new_left)
    setattr(node, options.right_field.name,     new_right)
    setattr(node, options.depth_field.name,     depth + depth_change)

# ===----------------------------------------------------------------------===

class TreeSessionExtension(sqlalchemy.orm.interfaces.SessionExtension):
  """An session extension handling insertion, deletion, and updates of tree
  nodes. This class is instantiated by the manager object, and the average
  developer need not bother himself with it.

  :param options:
    instance of :class:`TreeOptions`
  :param node_class:
    the mapped object class for tree nodes
  """
  def __init__(self, options, node_class):
    super(TreeSessionExtension, self).__init__()
    # Save the options for future use.
    self._tree_options = options
    self._node_class   = node_class

  def before_flush(self, session, flush_context, instances):
    "Just prior to a flush event, while we still have time to modify the flush plan."
    options = self._tree_options

    for node in session.new.union(session.dirty):
      if not isinstance(node, self._node_class):
        continue

      if hasattr(node, options.delayed_op_attr):
        pass

      elif (node in session.new or
            sqlalchemy.orm.attributes.get_history(
              node, options.parent_field_name).has_changes()):

        if (hasattr(options, 'order_with_respect_to') and
            len(options.order_with_respect_to)):
          raise NotImplementedError

        else:
          position = options.class_manager.POSITION_LAST_CHILD
          target   = getattr(node, options.parent_field_name)

        setattr(node, options.delayed_op_attr, (target, position))

# ===----------------------------------------------------------------------===
# End of File
# ===----------------------------------------------------------------------===
