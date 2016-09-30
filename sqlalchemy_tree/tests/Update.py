# -*- coding: utf-8 -*-
"""
    sqlalchemy_tree.tests.Update
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (C) 2012-2014 the SQLAlchemy-ORM-Tree authors and contributors
                <see AUTHORS file>.
    :license: BSD, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function, \
    with_statement, unicode_literals

from .helper import unittest, Named, db, get_tree_details
from .Named import TreeTestMixin


class UpdateTestCase(TreeTestMixin, unittest.TestCase):

    name_pattern = [
        (u"root1", {'id': 1, 'left': 1, 'right': 8, 'depth': 0}, [
            (u"child11", {'id': 1, 'left': 2, 'right': 3, 'depth': 1}, []),
            (u"child12", {'id': 1, 'left': 4, 'right': 7, 'depth': 1}, [
                (u"child13", {'id': 1, 'left': 5, 'right': 6, 'depth': 2}, []),
            ]),
        ])
    ]

    def _test_move_subtree_to_root(self, arg):
        result = [
            (u"root1", {'id': 1, 'left': 1, 'right': 4, 'depth': 0}, [
                (u"child11", {'id': 1, 'left': 2, 'right': 3, 'depth': 1}, []),
            ]),
            (u"child12", {'id': 2, 'left': 1, 'right': 4, 'depth': 0}, [
                (u"child13", {'id': 2, 'left': 2, 'right': 3, 'depth': 1}, []),
            ])
        ]

        node = db.session.query(Named).filter_by(name='child12').one()
        node.parent_id = None
        db.session.commit()
        self.assertEqual(get_tree_details(), result)

    def test_move_subtree_to_root_by_id(self):
        self._test_move_subtree_to_root('parent_id')

    def test_move_subtree_to_root_by_relationship(self):
        self._test_move_subtree_to_root('parent')

    def test_move_subtree_to_parent(self):
        result = [
            (u"root1", {'id': 1, 'left': 1, 'right': 8, 'depth': 0}, [
                (u"child11", {'id': 1, 'left': 2, 'right': 3, 'depth': 1}, []),
                (u"child12", {'id': 1, 'left': 4, 'right': 5, 'depth': 1}, []),
                (u"child13", {'id': 1, 'left': 6, 'right': 7, 'depth': 1}, []),
            ])
        ]

        node = db.session.query(Named).filter_by(name='child13').one()
        node.parent_id = db.session.query(Named).filter_by(name='root1').one().id
        db.session.commit()
        self.assertEqual(get_tree_details(), result)



def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(UpdateTestCase))
    return suite
