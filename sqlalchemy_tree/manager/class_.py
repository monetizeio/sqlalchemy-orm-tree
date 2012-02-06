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
      # NOTE: ``self._get_obj`` only exists on instance managers--this
      #       fallback only works from an instance manager of a node
      #       associated with a session.
      if session is None:
        session = sqlalchemy.orm.object_session(self._get_obj())
    return session.query(self.node_class) \
                  .filter(self.filter_root_node_of_node(*args, **kwargs))

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

# ===----------------------------------------------------------------------===
# End of File
# ===----------------------------------------------------------------------===
