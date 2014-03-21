# -*- coding: utf-8 -*-
"""
    sqlalchemy_tree.tests.Regression
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (C) 2012-2014 the SQLAlchemy-ORM-Tree authors and contributors
                <see AUTHORS file>.
    :license: BSD, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function, \
    with_statement, unicode_literals

from .helper import unittest, db, Named


class Regression__AddAllDifferentIds(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None
        db.metadata.drop_all()
        db.metadata.create_all()
        db.session = db.Session()

    def tearDown(self):
        db.session.close()

    def test_add_all(self):
        names = [u"root", u"child1", u"child2", u"root2"]
        nodes = [Named(name=x) for x in names]
        db.session.add_all(nodes)
        db.session.flush()
        self.assertEqual(
            [(1, 1, 2), (2, 1, 2), (3, 1, 2), (4, 1, 2)],
            sorted(map(lambda x: (x.tree_id, x.tree_left, x.tree_right), nodes)))


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Regression__AddAllDifferentIds))
    return suite
