#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    sqlalchemy_tree.types
    ~~~~~~~~~~~~~~~~~~~~~

    :copyright: (C) 2012-2014 the SQLAlchemy-ORM-Tree authors and contributors
                <see AUTHORS file>.
    :license: BSD, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function, \
    with_statement, unicode_literals

import sqlalchemy

__all__ = (
    'TreeIdType',
    'TreeEndpointType',
    'TreeLeftType',
    'TreeRightType',
    'TreeDepthType',
)


class TreeIntegerType(sqlalchemy.types.TypeDecorator):

    "Abstract base class implementing an integer type."
    impl = sqlalchemy.Integer


class TreeIdType(TreeIntegerType):

    "Integer field subtype representing an node's tree identifier."
    pass


class TreeEndpointType(TreeIntegerType):

    """Abstract base class of an integer implementing either a “left” or “right”
    field of a node."""
    pass


class TreeLeftType(TreeEndpointType):

    "Integer field subtype representing an node's “left” field."
    pass


class TreeRightType(TreeEndpointType):

    "Integer field subtype representing an node's “right” level."
    pass


class TreeDepthType(TreeIntegerType):

    "Integer field subtype representing an node's depth level."
    pass
