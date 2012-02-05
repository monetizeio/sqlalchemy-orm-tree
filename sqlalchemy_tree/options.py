#!/usr/bin/env python
# -*- coding: utf-8 -*-

# === sqlalchemy_tree.options ---------------------------------------------===
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

from .types import TreeIdType, TreeLeftType, TreeRightType, TreeDepthType

# ===----------------------------------------------------------------------===

class TreeOptions(object):
  """A container for options for one tree.

  :parameters:
    see :class:`TreeManager`.
  """
  def __init__(self,
               table,
               instance_manager_attr,
               parent_id_field=None,
               tree_id_field=None,
               left_field=None,
               right_field=None,
               depth_field=None):
    # Record required options for future use:
    self.table                 = table
    self._node_manager_attr    = None
    self.instance_manager_attr = instance_manager_attr
    self.delayed_op_attr       = None

    # FIXME: Add support for composite primary keys.
    assert len(table.primary_key.columns) == 1, \
           "Composite primary keys not supported"

    # Record the primary key column for future use:
    [self.pk_field] = table.primary_key.columns

    # The parent_id_field is auto-detected by joining the table with itself
    # and using the right-hand side of the resulting ON clause. This default
    # behavior may be overidden by specifying the desired JOIN column directly
    # or by name.
    if parent_id_field is None:
      # Auto-detect by building a self-JOIN command:
      self.parent_id_field = table.join(table).onclause.right
    elif isinstance(parent_id_field, basestring):
      # Column specified by name:
      self.parent_id_field = table.columns[parent_id_field]
    else:
      # Column specified directly:
      assert isinstance(parent_id_field, sqlalchemy.Column)
      assert parent_id_field.table is table
      self.parent_id_field = parent_id_field

    def _check_field(table, field, name, type_):
      """Check field argument (one of `tree_id_field`, `left_field`,
      `right_field`, or `depth_field`), convert it from field name to `Column`
      object (if needed), create the column object (again, if needed) and
      check the existing `Column` object for sanity."""
      columns = [getattr(table.columns, key) for key in table.columns.keys()]

      # If ‘field’ is not specified, we try to autodetect it from the columns
      # of the table based on ‘type_’.
      if field is None:
        candidates = filter(lambda c: isinstance(c.type, type_), columns)
        if len(candidates) == 1:
          field = candidates[0]
        else:
          field = 'tree_' + name

      # We assume that we'll be passed either a string or a SQLAlchemy Column
      # object (duck typing is not allowed). If what we're passed is a Column
      # object, we just need to check that
      if not isinstance(field, basestring):
        assert isinstance(field, sqlalchemy.Column)
        assert field.table is table

      # Otherwise we're passed a string, and either we find a field with that
      # name in the existing table Columns (likely but not necessarily if the
      # developer specified their own field name), or we'll have to create a
      # new column of the specified name and type, and insert it into the
      # table's column descriptions.
      elif field in table.columns:
        # Column exists:
        field = table.columns[field]
      else:
        # Column not found; create it:
        field = sqlalchemy.Column(field, type_(), nullable=False)
        table.append_column(field)
        # And return (since we know the following checks are redundant):
        return field

      # If we found the column or the developer specified it directly, we'll
      # do a quick sanity check to make sure that the column has the right
      # type and meta-attributes:
      assert isinstance(field.type, type_), \
             "The type of %s field should be %r" % (name, type_)
      assert not field.nullable, \
             "The %s field should not be nullable" % name

      # Field passes; return to caller:
      return field

    # Create (if necessary) or validate the properties of the core tree
    # fields:
    self.tree_id_field   = _check_field(table, tree_id_field, 'id',    TreeIdType)
    self.left_field      = _check_field(table, left_field,    'left',  TreeLeftType)
    self.right_field     = _check_field(table, right_field,   'right', TreeRightType)
    self.depth_field     = _check_field(table, depth_field,   'depth', TreeDepthType)
    self.required_fields = (
      self.tree_id_field,
      self.left_field,
      self.right_field,
      self.depth_field,
    )

    # To speed up operations, we create an index containing just the core
    # three fields that we care about for tree operations:
    self.indices = [
      sqlalchemy.Index(
        '__'.join((table.name,
                   self.tree_id_field.name,
                   self.left_field.name,
                   self.right_field.name)),
        self.tree_id_field,
        self.left_field,
        self.right_field,
        # NOTE: Originally there was a constraint that tree_id, left, and
        #       right be unique, simply as a sanity check. However on some
        #       database backends that don't properly support atomic queries
        #       this is causing an IntegrityError during tree operations.
        #unique=True
      ),
    ]
    map(table.append_constraint, self.indices)

  def class_mapped(self, manager):
    ""
    self.class_manager     = manager
    self.node_class        = manager.node_class
    self.node_manager_attr = self._get_node_manager_attr()
    self.delayed_op_attr   = self._get_delayed_op_attr()
    self.parent_field_name = self._get_parent_field_name()

  def _get_node_manager_attr(self):
    from .manager import TreeManager
    if self._node_manager_attr is None:
      self._node_manager_attr = filter(
        lambda x: isinstance(x[1], TreeManager),
        self.node_class.__dict__.items())[0][0]
    return self._node_manager_attr

  def _get_delayed_op_attr(self):
    if self.delayed_op_attr is None:
      self._get_node_manager_attr()
      self.delayed_op_attr = '__'.join(
        [self._node_manager_attr, 'delayed_op'])
    return self.delayed_op_attr

  def _get_parent_field_name(self):
    for prop in self.node_class._sa_class_manager.mapper.iterate_properties:
      if (len(prop.local_side) == 1 and
          prop.local_side[0].name == self.parent_id_field.name):
        return prop.key
    # FIXME: We should raise an error or something--the tree extension will
    #        not work property without a parent relationship defined.
    return None

  def order_by_clause(self):
    """Get an object applicable for usage as an argument for
    `Query.order_by()`. Used to sort subtree query by `tree_id` then
    `left`."""
    return sqlalchemy.sql.expression.asc(self.left_field)
    # FIXME: We should be sorting based on ``tree_id`` first, then ``left``
    #        (see disabled code below), however this was generating SQL not
    #        accepted by SQLite. Since most sorted queries are on just one
    #        tree in practice, ordering by just ``left`` will do for now. But
    #        when we have time we should find a cross-database method for
    #        ordering by multiple columns.
    #
    #return sqlalchemy.sql.expression.ClauseList(
    #  sqlalchemy.sql.expression.asc(self.tree_id_field),
    #  sqlalchemy.sql.expression.asc(self.left_field),
    #)

# ===----------------------------------------------------------------------===
# End of File
# ===----------------------------------------------------------------------===
