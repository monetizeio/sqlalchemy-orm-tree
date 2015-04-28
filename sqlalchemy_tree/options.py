#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    sqlalchemy_tree.options
    ~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (C) 2012-2014 the SQLAlchemy-ORM-Tree authors and contributors
                <see AUTHORS file>.
    :license: BSD, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function, \
    with_statement, unicode_literals

import sqlalchemy

from .types import TreeIdType, TreeLeftType, TreeRightType, TreeDepthType
from ._compat import string_types, py2map as map


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
                 depth_field=None,
                 _attach_columns=True):
        # Record required options for future use:
        self.table = table
        self._node_manager_attr = None
        self.instance_manager_attr = instance_manager_attr
        self.delayed_op_attr = None

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
        elif isinstance(parent_id_field, string_types):
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
            columns = [getattr(table.columns, key)
                       for key in table.columns.keys()]

            # If ‘field’ is not specified, we try to autodetect it from the columns
            # of the table based on ‘type_’.
            if field is None:
                candidates = [c for c in columns if isinstance(c.type, type_)]
                if len(candidates) == 1:
                    field = candidates[0]
                else:
                    field = 'tree_' + name

            # We assume that we'll be passed either a string or a SQLAlchemy Column
            # object (duck typing is not allowed). If what we're passed is a Column
            # object, we just need to check that
            if not isinstance(field, string_types):
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
                if _attach_columns:
                    table.append_column(field)
                # And return (since we know the following checks are
                # redundant):
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
        self.tree_id_field = _check_field(
            table, tree_id_field, 'id', TreeIdType)
        self.left_field = _check_field(
            table, left_field, 'left', TreeLeftType)
        self.right_field = _check_field(
            table, right_field, 'right', TreeRightType)
        self.depth_field = _check_field(
            table, depth_field, 'depth', TreeDepthType)
        self.required_fields = (
            self.tree_id_field,
            self.left_field,
            self.right_field,
            self.depth_field,
        )

        if _attach_columns:
            self.attach_indices()

    def attach_indices(self):
        # To speed up operations, we create an index containing just the core
        # three fields that we care about for tree operations:
        self.indices = [
            sqlalchemy.Index(
                '__'.join((self.table.name,
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
                # unique=True
            ),
        ]
        map(self.table.append_constraint, self.indices)

    def class_mapped(self, manager):
        ""
        self.class_manager = manager
        self.node_class = manager.node_class
        self.node_manager_attr = self._get_node_manager_attr()
        self.delayed_op_attr = self._get_delayed_op_attr()
        self.parent_field_name = self._get_parent_field_name()

    def _get_node_manager_attr(self):
        from .manager import TreeManager
        if self._node_manager_attr is None:
            self._node_manager_attr = [
                x for x in
                self.node_class.__dict__.items()
                if isinstance(x[1], TreeManager)
            ][0][0]
        return self._node_manager_attr

    def _get_delayed_op_attr(self):
        if self.delayed_op_attr is None:
            self._get_node_manager_attr()
            self.delayed_op_attr = '__'.join(
                [self._node_manager_attr, 'delayed_op'])
        return self.delayed_op_attr

    def _get_parent_field_name(self):
        for prop in self.node_class._sa_class_manager.mapper.iterate_properties:
            if (len(getattr(prop, 'local_side', [])) == 1 and
                    prop.local_side[0].name == self.parent_id_field.name):
                return prop.key
        for prop in self.node_class._sa_class_manager.mapper.iterate_properties:
            if (getattr(prop, 'remote_side', None) is not None and
                    getattr(prop.remote_side, 'name', None) == self.pk_field.name):
                return prop.key
            # Above test works for SQLAlchemy 0.7, the one below for 0.8
            if (len(getattr(prop, 'remote_side', [])) == 1 and
                    self.pk_field in prop.remote_side):
                return prop.key
        raise ValueError(
            u"could not auto-detect parent field name; tree extension will not "
            u"work property without a parent relationship defined")

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
        # return sqlalchemy.sql.expression.ClauseList(
        #  sqlalchemy.sql.expression.asc(self.tree_id_field),
        #  sqlalchemy.sql.expression.asc(self.left_field),
        #)
