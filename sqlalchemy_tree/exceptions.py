#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    sqlalchemy_tree.exceptions
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (C) 2012-2014 the SQLAlchemy-ORM-Tree authors and contributors
                <see AUTHORS file>.
    :license: BSD, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function, \
    with_statement, unicode_literals


__all__ = [
    'InvalidMoveError',
]


class InvalidMoveError(Exception):

    """An invalid node move was attempted. For example, attempting to make a
    node a child of itself."""
    pass
