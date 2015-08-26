# -*- coding: utf-8 -*-
"""
    sqlalchemy_tree.tests.Insert
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (C) 2012-2014 the SQLAlchemy-ORM-Tree authors and contributors
                <see AUTHORS file>.
    :license: BSD, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function, \
    with_statement, unicode_literals

from .helper import unittest, Named, db, get_tree_details
from .Named import TreeTestMixin


class InsertTestCase(TreeTestMixin, unittest.TestCase):

    name_pattern = []

    def test_insert_at_root(self):
        result = [
            (u'test', {u'depth': 0, u'right': 2, u'id': 1, u'left': 1}, [])
        ]
        new = Named(name="test")
        db.session.add(new)
        db.session.commit()
        self.assertEqual(get_tree_details(), result)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(InsertTestCase))
    return suite
