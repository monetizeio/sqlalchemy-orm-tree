# -*- coding: utf-8 -*-
"""
    sqlalchemy_tree.tests.Named
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (C) 2012-2014 the SQLAlchemy-ORM-Tree authors and contributors
                <see AUTHORS file>.
    :license: BSD, see LICENSE for more details.
"""

import sqlalchemy

import sqlalchemy_tree

from .. import TreeClassManager, TreeInstanceManager

from .helper import unittest, TreeTestMixin, db, Named, permutations



class NamedTestCase(TreeTestMixin, unittest.TestCase):
  "Provides general unit tests of the SQLAlchemy tree extension using the `named` table."
  name_pattern = [
    (u"root1", {'id':1, 'left':1, 'right':8, 'depth':0}, [
      (u"child11", {'id':1, 'left':2, 'right':3, 'depth':1}, []),
      (u"child12", {'id':1, 'left':4, 'right':5, 'depth':1}, []),
      (u"child13", {'id':1, 'left':6, 'right':7, 'depth':1}, []),
    ]),
    (u"root2", {'id':2, 'left':1, 'right':20, 'depth':0}, [
      (u"child21", {'id':2, 'left':2, 'right':15, 'depth':1}, [
        (u"child211", {'id':2, 'left':3, 'right':4, 'depth':2}, []),
        (u"child212", {'id':2, 'left':5, 'right':14, 'depth':2}, [
          (u"child2121", {'id':2, 'left':6, 'right':7, 'depth':3}, []),
          (u"child2122", {'id':2, 'left':8, 'right':13, 'depth':3}, [
            (u"child21221", {'id':2, 'left':9, 'right':10, 'depth':4}, []),
            (u"child21222", {'id':2, 'left':11, 'right':12, 'depth':4}, []),
          ]),
        ]),
      ]),
      (u"child22", {'id':2, 'left':16, 'right':17, 'depth':1}, []),
      (u"child23", {'id':2, 'left':18, 'right':19, 'depth':1}, []),
    ]),
    (u"root3", {'id':3, 'left':1, 'right':2, 'depth':0}, []),
  ]
  result_static = [
    (u"root1", {
      'ancestors': [],
      'parent': [],
      'previous-siblings': [],
      'next-siblings': ["root2","root3"],
      'children': ["child11","child12","child13"],
      'descendants': ["child11","child12","child13"],
      'leaf-nodes': ["child11","child12","child13"]}),
    (u"child11", {
      'ancestors': ["root1"],
      'parent': ["root1"],
      'previous-siblings': [],
      'next-siblings': ["child12", "child13"],
      'children': [],
      'descendants': [],
      'leaf-nodes': []}),
    (u"child12", {
      'ancestors': ["root1"],
      'parent': ["root1"],
      'previous-siblings': ["child11"],
      'next-siblings': ["child13"],
      'children': [],
      'descendants': [],
      'leaf-nodes': []}),
    (u"child13", {
      'ancestors': ["root1"],
      'parent': ["root1"],
      'previous-siblings': ["child11","child12"],
      'next-siblings': [],
      'children': [],
      'descendants': [],
      'leaf-nodes': []}),
    (u"root2", {
      'ancestors': [],
      'parent': [],
      'previous-siblings': ["root1"],
      'next-siblings': ["root3"],
      'children': ["child21","child22","child23"],
      'descendants': [
        "child21","child211","child212","child2121","child2122","child21221",
        "child21222","child22","child23"],
      'leaf-nodes': ["child211","child2121","child21221","child21222",
        "child22","child23"]}),
    (u"child21", {
      'ancestors': ["root2"],
      'parent': ["root2"],
      'previous-siblings': [],
      'next-siblings': ["child22","child23"],
      'children': ["child211","child212"],
      'descendants': [
        "child211","child212","child2121","child2122","child21221",
        "child21222"],
      'leaf-nodes': ["child211","child2121","child21221","child21222"]}),
    (u"child211", {
      'ancestors': ["root2","child21"],
      'parent': ["child21"],
      'previous-siblings': [],
      'next-siblings': ["child212"],
      'children': [],
      'descendants': [],
      'leaf-nodes': []}),
    (u"child212", {
      'ancestors': ["root2","child21"],
      'parent': ["child21"],
      'previous-siblings': ["child211"],
      'next-siblings': [],
      'children': ["child2121","child2122"],
      'descendants': ["child2121","child2122","child21221","child21222"],
      'leaf-nodes': ["child2121","child21221","child21222"]}),
    (u"child2121", {
      'ancestors': ["root2","child21","child212"],
      'parent': ["child212"],
      'previous-siblings': [],
      'next-siblings': ["child2122"],
      'children': [],
      'descendants': [],
      'leaf-nodes': []}),
    (u"child2122", {
      'ancestors': ["root2","child21","child212"],
      'parent': ["child212"],
      'previous-siblings': ["child2121"],
      'next-siblings': [],
      'children': ["child21221","child21222"],
      'descendants': ["child21221","child21222"],
      'leaf-nodes': ["child21221","child21222"]}),
    (u"child21221", {
      'ancestors': ["root2","child21","child212","child2122"],
      'parent': ["child2122"],
      'previous-siblings': [],
      'next-siblings': ["child21222"],
      'children': [],
      'descendants': [],
      'leaf-nodes': []}),
    (u"child21222", {
      'ancestors': ["root2","child21","child212","child2122"],
      'parent': ["child2122"],
      'previous-siblings': ["child21221"],
      'next-siblings': [],
      'children': [],
      'descendants': [],
      'leaf-nodes': []}),
    (u"child22", {
      'ancestors': ["root2"],
      'parent': ["root2"],
      'previous-siblings': ["child21"],
      'next-siblings': ["child23"],
      'children': [],
      'descendants': [],
      'leaf-nodes': []}),
    (u"child23", {
      'ancestors': ["root2"],
      'parent': ["root2"],
      'previous-siblings': ["child21","child22"],
      'next-siblings': [],
      'children': [],
      'descendants': [],
      'leaf-nodes': []}),
    (u"root3", {
      'ancestors': [],
      'parent': [],
      'previous-siblings': ["root1","root2"],
      'next-siblings': [],
      'children': [],
      'descendants': [],
      'leaf-nodes': []}),
  ]
  def test_named_hasattr_tree_id(self):
    "‘named’ table has extra column ‘tree_id’"
    self.assertTrue(hasattr(Named, 'tree_id'))
  def test_named_hasattr_tree_left(self):
    "‘named’ table has extra column ‘tree_left’"
    self.assertTrue(hasattr(Named, 'tree_left'))
  def test_named_hasattr_tree_right(self):
    "‘named’ table has extra column ‘tree_right’"
    self.assertTrue(hasattr(Named, 'tree_right'))
  def test_named_hasattr_tree_depth(self):
    "‘named’ table has extra column ‘tree_depth’"
    self.assertTrue(hasattr(Named, 'tree_depth'))
  def test_named_tree_yields_class_manager(self):
    "Named.tree returns an TreeClassManager"
    self.assertTrue(isinstance(Named.tree, TreeClassManager))
  def test_named_tree_yields_instance_manager(self):
    "Named().tree returns an TreeClassManager"
    self.assertTrue(isinstance(Named().tree, TreeInstanceManager))
  def test_pk_field(self):
    "Named.tree.pk_field returns ‘id’ column."
    # Class manager:
    self.assertIsInstance(Named.tree.pk_field, sqlalchemy.schema.Column)
    self.assertEqual(Named.tree.pk_field.name, 'id')
    # Instance manager:
    self.assertIsInstance(Named().tree.pk_field, sqlalchemy.schema.Column)
    self.assertEqual(Named().tree.pk_field.name, 'id')
  def test_parent_id_field(self):
    "Named.tree.parent_id_field returns ‘parent_id’ column."
    # Class manager:
    self.assertIsInstance(Named.tree.parent_id_field, sqlalchemy.schema.Column)
    self.assertEqual(Named.tree.parent_id_field.name, 'parent_id')
    # Instance manager:
    self.assertIsInstance(Named().tree.parent_id_field, sqlalchemy.schema.Column)
    self.assertEqual(Named().tree.parent_id_field.name, 'parent_id')
  def test_parent_field_name(self):
    "Named.tree.parent_field_name returns name of ‘parent’ relationship."
    # Class manager:
    self.assertEqual(Named.tree.parent_field_name, 'parent')
    # Instance manager:
    self.assertEqual(Named().tree.parent_field_name, 'parent')
  def test_tree_id_field(self):
    "Named().tree.tree_id_field returns ‘tree_id’ column."
    # Class manager:
    self.assertIsInstance(Named.tree.tree_id_field,      sqlalchemy.schema.Column)
    self.assertIsInstance(Named.tree.tree_id_field.type, sqlalchemy_tree.types.TreeIdType)
    self.assertEqual(Named.tree.tree_id_field.name,      'tree_id')
    # Instance manager:
    self.assertIsInstance(Named().tree.tree_id_field,      sqlalchemy.schema.Column)
    self.assertIsInstance(Named().tree.tree_id_field.type, sqlalchemy_tree.types.TreeIdType)
    self.assertEqual(Named().tree.tree_id_field.name,      'tree_id')
  def test_left_field(self):
    "Named().tree.left_field returns ‘tree_left’ column."
    # Class manager:
    self.assertIsInstance(Named.tree.left_field,      sqlalchemy.schema.Column)
    self.assertIsInstance(Named.tree.left_field.type, sqlalchemy_tree.types.TreeLeftType)
    self.assertEqual(Named.tree.left_field.name,      'tree_left')
    # Instance manager:
    self.assertIsInstance(Named().tree.left_field,      sqlalchemy.schema.Column)
    self.assertIsInstance(Named().tree.left_field.type, sqlalchemy_tree.types.TreeLeftType)
    self.assertEqual(Named().tree.left_field.name,      'tree_left')
  def test_right_field(self):
    "Named().tree.right_field returns ‘tree_right’ column."
    # Class manager:
    self.assertIsInstance(Named.tree.right_field,      sqlalchemy.schema.Column)
    self.assertIsInstance(Named.tree.right_field.type, sqlalchemy_tree.types.TreeRightType)
    self.assertEqual(Named.tree.right_field.name,      'tree_right')
    # Instance manager:
    self.assertIsInstance(Named().tree.right_field,      sqlalchemy.schema.Column)
    self.assertIsInstance(Named().tree.right_field.type, sqlalchemy_tree.types.TreeRightType)
    self.assertEqual(Named().tree.right_field.name,      'tree_right')
  def test_depth_field(self):
    "Named().tree.depth_field returns ‘tree_depth’ column."
    # Class manager:
    self.assertIsInstance(Named.tree.depth_field,      sqlalchemy.schema.Column)
    self.assertIsInstance(Named.tree.depth_field.type, sqlalchemy_tree.types.TreeDepthType)
    self.assertEqual(Named.tree.depth_field.name,      'tree_depth')
    # Instance manager:
    self.assertIsInstance(Named().tree.depth_field,      sqlalchemy.schema.Column)
    self.assertIsInstance(Named().tree.depth_field.type, sqlalchemy_tree.types.TreeDepthType)
    self.assertEqual(Named().tree.depth_field.name,      'tree_depth')
  def test_pk_property(self):
    "Named().tree.pk returns ‘id’ value."
    for node in db.session.query(Named).all():
      self.assertEqual(node.id, node.tree.pk)
  def test_parent_id_property(self):
    "Named().tree.parent_id returns ‘parent_id’ value."
    for node in db.session.query(Named).all():
      self.assertEqual(node.parent_id, node.tree.parent_id)
  def test_parent_property(self):
    "Named().tree.parent returns ‘parent’ related object."
    for node in db.session.query(Named).all():
      self.assertEqual(node.parent, node.tree.parent)
  def test_tree_id_left_right_depth_properties(self):
    "tree_id, left, right, and depth attributes of Named().tree return corresponding tree properties."
    def _helper(name, params, children):
      node = db.session.query(Named).filter_by(name=name).one()
      self.assertEqual(node.tree.tree_id, params['id'])
      self.assertEqual(node.tree.left,    params['left'])
      self.assertEqual(node.tree.right,   params['right'])
      self.assertEqual(node.tree.depth,   params['depth'])
      for pattern in children:
        _helper(*pattern)
    for pattern in self.name_pattern:
      _helper(*pattern)
  def test_filter_root_node(self):
    "Verify the root nodes against the expected values"
    for node in db.session.query(Named).all():
      root = db.session.query(Named) \
                       .filter(node.tree.filter_root_node()) \
                       .one()
      self.assertEqual(root.tree.depth,   0)
      self.assertEqual(root.tree.tree_id, node.tree.tree_id)
  def test_query_root_node(self):
    "Verify the root nodes against the expected values"
    for node in db.session.query(Named).all():
      root = node.tree.query_root_node().one()
      self.assertEqual(root.tree.depth,   0)
      self.assertEqual(root.tree.tree_id, node.tree.tree_id)
  def test_root_node_property(self):
    "Verify the root nodes against the expected values"
    for node in db.session.query(Named).all():
      root = node.tree.root_node
      self.assertEqual(root.tree.depth,   0)
      self.assertEqual(root.tree.tree_id, node.tree.tree_id)
  def test_filter_root_nodes(self):
    "Verify the root nodes against the expected values"
    expected = sorted([x[0] for x in self.name_pattern])
    self.assertEqual(expected, [x.name for x in
      db.session.query(Named)
                .filter(Named.tree.filter_root_nodes())
                .order_by(Named.name)
                .all()])
  def test_query_root_nodes(self):
    "Verify the root nodes against the expected values"
    expected = sorted([x[0] for x in self.name_pattern])
    self.assertEqual(expected, [x.name for x in
      Named.tree.query_root_nodes(session=db.session)
                .order_by(Named.name)
                .all()])
  def test_filter_root_node_by_tree_id(self):
    "Verify root node from tree id against expected value"
    def _process_node(root_name, node_name, children):
      node = db.session.query(Named).filter_by(name=node_name).one()
      self.assertEqual(root_name,
        db.session.query(Named)
                  .filter(Named.tree.filter_root_node_by_tree_id(node.tree_id))
                  .one().name)
      for child_name, values, grandchildren in children:
        _process_node(root_name, child_name, grandchildren)
    for root_name, values, children in self.name_pattern:
      _process_node(root_name, root_name, children)
  def test_query_root_node_by_tree_id(self):
    "Verify root node from tree id against expected value"
    def _process_node(root_name, node_name, children):
      node = db.session.query(Named).filter_by(name=node_name).one()
      self.assertEqual(root_name,
        Named.tree.query_root_node_by_tree_id(node.tree_id, session=db.session)
                  .one().name)
      self.assertEqual(root_name,
        node.tree.query_root_node_by_tree_id(node.tree_id)
                 .one().name)
      for child_name, values, grandchildren in children:
        _process_node(root_name, child_name, grandchildren)
    for root_name, values, children in self.name_pattern:
      _process_node(root_name, root_name, children)
  def test_filter_root_node_of_node(self):
    "Verify root node from tree id against expected value"
    def _process_node(root_name, node_name, children):
      node = db.session.query(Named).filter_by(name=node_name).one()
      self.assertEqual(root_name,
        db.session.query(Named)
                  .filter(Named.tree.filter_root_node_of_node(node))
                  .one().name)
      for child_name, values, grandchildren in children:
        _process_node(root_name, child_name, grandchildren)
    for root_name, values, children in self.name_pattern:
      _process_node(root_name, root_name, children)
  def test_query_root_node_of_node(self):
    "Verify root node from tree id against expected value"
    def _process_node(root_name, node_name, children):
      node = db.session.query(Named).filter_by(name=node_name).one()
      self.assertEqual(root_name,
        Named.tree.query_root_node_of_node(node, session=db.session)
                  .one().name)
      self.assertEqual(root_name,
        node.tree.query_root_node_of_node(node)
                 .one().name)
      for child_name, values, grandchildren in children:
        _process_node(root_name, child_name, grandchildren)
    for root_name, values, children in self.name_pattern:
      _process_node(root_name, root_name, children)
  def test_filter_ancestors(self):
    "Verify the ancestors of each node against expected values"
    for pattern in self.result_static:
      name, result = pattern
      obj = db.session.query(Named).filter_by(name=name).one()
      self.assertEqual(result['ancestors'],
        map(lambda x:x.name,
          db.session.query(Named)
            .filter(obj.tree.filter_ancestors())
            .order_by(Named.tree).all()))
      self.assertEqual(result['ancestors'] + [obj.name],
        map(lambda x:x.name,
          db.session.query(Named)
            .filter(obj.tree.filter_ancestors(include_self=True))
            .order_by(Named.tree).all()))
  def test_query_ancestors(self):
    "Verify the ancestors of each node against expected values"
    for pattern in self.result_static:
      name, result = pattern
      obj = db.session.query(Named).filter_by(name=name).one()
      self.assertEqual(result['ancestors'],
        map(lambda x:x.name,
            obj.tree.query_ancestors().order_by(Named.tree).all()))
      self.assertEqual(result['ancestors'] + [obj.name],
        map(lambda x:x.name,
            obj.tree.query_ancestors(include_self=True).order_by(Named.tree).all()))
  def test_filter_parent(self):
    "Verify the parent of each node against the expected value"
    for pattern in self.result_static:
      name, result = pattern
      obj = db.session.query(Named).filter_by(name=name).one()
      self.assertEqual(result['parent'],
        map(lambda x:x.name,
          db.session.query(Named).filter(obj.tree.filter_parent()).all()))
  def test_filter_parent_of_node(self):
    "Verify the parent of each node against the expected value"
    for pattern in self.result_static:
      name, result = pattern
      obj = db.session.query(Named).filter_by(name=name).one()
      self.assertEqual(result['parent'],
        map(lambda x:x and x.name or None,
          db.session.query(Named).filter(Named.tree.filter_parent_of_node(obj)).all()))
  def test_query_parent_of_node(self):
    "Verify the parent of each node against the expected value"
    for pattern in self.result_static:
      name, result = pattern
      obj = db.session.query(Named).filter_by(name=name).one()
      self.assertEqual(result['parent'],
        map(lambda x:x.name,
          Named.tree.query_parent_of_node(obj).all()))
  def test_filter_siblings(self):
    "Verify the siblings of each node against the expected values"
    for pattern in self.result_static:
      name, result = pattern
      obj = db.session.query(Named).filter_by(name=name).one()
      self.assertEqual(result['previous-siblings'] + result['next-siblings'],
        map(lambda x:x.name,
          db.session.query(Named).filter(obj.tree.filter_siblings()).all()))
      self.assertEqual(result['previous-siblings'] + [name] + result['next-siblings'],
        map(lambda x:x.name,
          db.session.query(Named).filter(obj.tree.filter_siblings(include_self=True)).all()))
  def test_query_siblings(self):
    "Verify the siblings of each node against the expected values"
    for pattern in self.result_static:
      name, result = pattern
      obj = db.session.query(Named).filter_by(name=name).one()
      self.assertEqual(result['previous-siblings'] + result['next-siblings'],
        map(lambda x:x.name, obj.tree.query_siblings().all()))
      self.assertEqual(result['previous-siblings'] + [name] + result['next-siblings'],
        map(lambda x:x.name, obj.tree.query_siblings(include_self=True).all()))
  def test_filter_previous_siblings(self):
    "Verify the siblings of each node against the expected values"
    for pattern in self.result_static:
      name, result = pattern
      obj = db.session.query(Named).filter_by(name=name).one()
      self.assertEqual(result['previous-siblings'],
        map(lambda x:x.name,
          db.session.query(Named).filter(obj.tree.filter_previous_siblings()).all()))
      self.assertEqual(result['previous-siblings'] + [name],
        map(lambda x:x.name,
          db.session.query(Named).filter(obj.tree.filter_previous_siblings(include_self=True)).all()))
  def test_query_previous_siblings(self):
    "Verify the siblings of each node against the expected values"
    for pattern in self.result_static:
      name, result = pattern
      obj = db.session.query(Named).filter_by(name=name).one()
      self.assertEqual(result['previous-siblings'],
        map(lambda x:x.name, obj.tree.query_previous_siblings().all()))
      self.assertEqual(result['previous-siblings'] + [name],
        map(lambda x:x.name, obj.tree.query_previous_siblings(include_self=True).all()))
  def test_filter_next_siblings(self):
    "Verify the siblings of each node against the expected values"
    for pattern in self.result_static:
      name, result = pattern
      obj = db.session.query(Named).filter_by(name=name).one()
      self.assertEqual(result['next-siblings'],
        map(lambda x:x.name,
          db.session.query(Named).filter(obj.tree.filter_next_siblings()).all()))
      self.assertEqual([name] + result['next-siblings'],
        map(lambda x:x.name,
          db.session.query(Named).filter(obj.tree.filter_next_siblings(include_self=True)).all()))
  def test_query_next_siblings(self):
    "Verify the siblings of each node against the expected values"
    for pattern in self.result_static:
      name, result = pattern
      obj = db.session.query(Named).filter_by(name=name).one()
      self.assertEqual(result['next-siblings'],
        map(lambda x:x.name, obj.tree.query_next_siblings().all()))
      self.assertEqual([name] + result['next-siblings'],
        map(lambda x:x.name, obj.tree.query_next_siblings(include_self=True).all()))
  def test_previous_sibling_property(self):
    "Verify the previous sibling of each node against the expected value"
    for pattern in self.result_static:
      name, result = pattern
      obj = db.session.query(Named).filter_by(name=name).one()
      sibling = obj.tree.previous_sibling
      if sibling is None:
        self.assertFalse(result['previous-siblings'])
      else:
        self.assertEqual(result['previous-siblings'][-1], sibling.name)
  def test_next_sibling_property(self):
    "Verify the next sibling of each node against the expected value"
    for pattern in self.result_static:
      name, result = pattern
      obj = db.session.query(Named).filter_by(name=name).one()
      sibling = obj.tree.next_sibling
      if sibling is None:
        self.assertFalse(result['next-siblings'])
      else:
        self.assertEqual(result['next-siblings'][0], sibling.name)
  def test_filter_siblings_of_node(self):
    "Verify the siblings of each node against expected values"
    for pattern in self.result_static:
      name, result = pattern
      obj = db.session.query(Named).filter_by(name=name).one()
      self.assertEqual(result['previous-siblings'] + result['next-siblings'],
        map(lambda x:x.name,
          db.session.query(Named)
            .filter(Named.tree.filter_siblings_of_node(obj))
            .order_by(Named.tree).all()))
      self.assertEqual(result['previous-siblings'] + [obj.name] + result['next-siblings'],
        map(lambda x:x.name,
          db.session.query(Named)
            .filter(Named.tree.filter_siblings_of_node(obj, include_self=True))
            .order_by(Named.tree).all()))
    # permutations() is used instead of combinations() to ensure that the
    # result is irrespective of the ordering of the nodes:
    for results in permutations(self.result_static, 2):
      names         = [x[0] for x in results]
      nodes         = [db.session.query(Named).filter_by(name=x).one() for x in names]
      siblings      = [set(x[1]['previous-siblings'] + x[1]['next-siblings']) for x in results]
      siblings2     = map(lambda x:x[1].union(set([x[0]])), zip(names, siblings))
      union         = reduce(lambda l,r:l.union(r),        siblings)
      union2        = reduce(lambda l,r:l.union(r),        siblings2)
      intersection  = reduce(lambda l,r:l.intersection(r), siblings)
      intersection2 = reduce(lambda l,r:l.intersection(r), siblings2)
      self.assertEqual(union,
        set(map(
          lambda node:node.name,
          db.session.query(Named)
            .filter(Named.tree.filter_siblings_of_node(*nodes))
            .all())))
      self.assertEqual(union2,
        set(map(
          lambda node:node.name,
          db.session.query(Named)
            .filter(Named.tree.filter_siblings_of_node(*nodes, include_self=True))
            .all())))
      self.assertEqual(intersection,
        set(map(
          lambda node:node.name,
          db.session.query(Named)
            .filter(Named.tree.filter_siblings_of_node(*nodes, disjoint=False))
            .all())))
      self.assertEqual(intersection2,
        set(map(
          lambda node:node.name,
          db.session.query(Named)
            .filter(Named.tree.filter_siblings_of_node(*nodes, include_self=True, disjoint=False))
            .all())))
  def test_query_siblings_of_node(self):
    "Verify the siblings of each node against expected values"
    for pattern in self.result_static:
      name, result = pattern
      obj = db.session.query(Named).filter_by(name=name).one()
      self.assertEqual(result['previous-siblings'] + result['next-siblings'],
        map(lambda x:x.name,
          Named.tree.query_siblings_of_node(obj)
            .order_by(Named.tree).all()))
      self.assertEqual(result['previous-siblings'] + [obj.name] + result['next-siblings'],
        map(lambda x:x.name,
          Named.tree.query_siblings_of_node(obj, include_self=True)
            .order_by(Named.tree).all()))
    # permutations() is used instead of combinations() to ensure that the
    # result is irrespective of the ordering of the nodes:
    for results in permutations(self.result_static, 2):
      names         = [x[0] for x in results]
      nodes         = [db.session.query(Named).filter_by(name=x).one() for x in names]
      siblings      = [set(x[1]['previous-siblings'] + x[1]['next-siblings']) for x in results]
      siblings2     = map(lambda x:x[1].union(set([x[0]])), zip(names, siblings))
      union         = reduce(lambda l,r:l.union(r),        siblings)
      union2        = reduce(lambda l,r:l.union(r),        siblings2)
      intersection  = reduce(lambda l,r:l.intersection(r), siblings)
      intersection2 = reduce(lambda l,r:l.intersection(r), siblings2)
      self.assertEqual(union,
        set(map(
          lambda node:node.name,
          Named.tree.query_siblings_of_node(*nodes)
            .all())))
      self.assertEqual(union2,
        set(map(
          lambda node:node.name,
          Named.tree.query_siblings_of_node(*nodes, include_self=True)
            .all())))
      self.assertEqual(intersection,
        set(map(
          lambda node:node.name,
          Named.tree.query_siblings_of_node(*nodes, disjoint=False)
            .all())))
      self.assertEqual(intersection2,
        set(map(
          lambda node:node.name,
          Named.tree.query_siblings_of_node(*nodes, include_self=True, disjoint=False)
            .all())))
  def test_filter_previous_siblings_of_node(self):
    "Verify the siblings of each node against expected values"
    for pattern in self.result_static:
      name, result = pattern
      obj = db.session.query(Named).filter_by(name=name).one()
      self.assertEqual(result['previous-siblings'],
        map(lambda x:x.name,
          db.session.query(Named)
            .filter(Named.tree.filter_previous_siblings_of_node(obj))
            .order_by(Named.tree).all()))
      self.assertEqual(result['previous-siblings'] + [obj.name],
        map(lambda x:x.name,
          db.session.query(Named)
            .filter(Named.tree.filter_previous_siblings_of_node(obj, include_self=True))
            .order_by(Named.tree).all()))
    # permutations() is used instead of combinations() to ensure that the
    # result is irrespective of the ordering of the nodes:
    for results in permutations(self.result_static, 2):
      names         = [x[0] for x in results]
      nodes         = [db.session.query(Named).filter_by(name=x).one() for x in names]
      siblings      = [set(x[1]['previous-siblings']) for x in results]
      siblings2     = map(lambda x:x[1].union(set([x[0]])), zip(names, siblings))
      union         = reduce(lambda l,r:l.union(r),        siblings)
      union2        = reduce(lambda l,r:l.union(r),        siblings2)
      intersection  = reduce(lambda l,r:l.intersection(r), siblings)
      intersection2 = reduce(lambda l,r:l.intersection(r), siblings2)
      self.assertEqual(union,
        set(map(
          lambda node:node.name,
          db.session.query(Named)
            .filter(Named.tree.filter_previous_siblings_of_node(*nodes))
            .all())))
      self.assertEqual(union2,
        set(map(
          lambda node:node.name,
          db.session.query(Named)
            .filter(Named.tree.filter_previous_siblings_of_node(*nodes, include_self=True))
            .all())))
      self.assertEqual(intersection,
        set(map(
          lambda node:node.name,
          db.session.query(Named)
            .filter(Named.tree.filter_previous_siblings_of_node(*nodes, disjoint=False))
            .all())))
      self.assertEqual(intersection2,
        set(map(
          lambda node:node.name,
          db.session.query(Named)
            .filter(Named.tree.filter_previous_siblings_of_node(*nodes, include_self=True, disjoint=False))
            .all())))
  def test_query_previous_siblings_of_node(self):
    "Verify the siblings of each node against expected values"
    for pattern in self.result_static:
      name, result = pattern
      obj = db.session.query(Named).filter_by(name=name).one()
      self.assertEqual(result['previous-siblings'],
        map(lambda x:x.name,
          Named.tree.query_previous_siblings_of_node(obj)
            .order_by(Named.tree).all()))
      self.assertEqual(result['previous-siblings'] + [obj.name],
        map(lambda x:x.name,
          Named.tree.query_previous_siblings_of_node(obj, include_self=True)
            .order_by(Named.tree).all()))
    # permutations() is used instead of combinations() to ensure that the
    # result is irrespective of the ordering of the nodes:
    for results in permutations(self.result_static, 2):
      names         = [x[0] for x in results]
      nodes         = [db.session.query(Named).filter_by(name=x).one() for x in names]
      siblings      = [set(x[1]['previous-siblings']) for x in results]
      siblings2     = map(lambda x:x[1].union(set([x[0]])), zip(names, siblings))
      union         = reduce(lambda l,r:l.union(r),        siblings)
      union2        = reduce(lambda l,r:l.union(r),        siblings2)
      intersection  = reduce(lambda l,r:l.intersection(r), siblings)
      intersection2 = reduce(lambda l,r:l.intersection(r), siblings2)
      self.assertEqual(union,
        set(map(
          lambda node:node.name,
          Named.tree.query_previous_siblings_of_node(*nodes)
            .all())))
      self.assertEqual(union2,
        set(map(
          lambda node:node.name,
          Named.tree.query_previous_siblings_of_node(*nodes, include_self=True)
            .all())))
      self.assertEqual(intersection,
        set(map(
          lambda node:node.name,
          Named.tree.query_previous_siblings_of_node(*nodes, disjoint=False)
            .all())))
      self.assertEqual(intersection2,
        set(map(
          lambda node:node.name,
          Named.tree.query_previous_siblings_of_node(*nodes, include_self=True, disjoint=False)
            .all())))
  def test_filter_next_siblings_of_node(self):
    "Verify the siblings of each node against expected values"
    for pattern in self.result_static:
      name, result = pattern
      obj = db.session.query(Named).filter_by(name=name).one()
      self.assertEqual(result['next-siblings'],
        map(lambda x:x.name,
          db.session.query(Named)
            .filter(Named.tree.filter_next_siblings_of_node(obj))
            .order_by(Named.tree).all()))
      self.assertEqual([obj.name] + result['next-siblings'],
        map(lambda x:x.name,
          db.session.query(Named)
            .filter(Named.tree.filter_next_siblings_of_node(obj, include_self=True))
            .order_by(Named.tree).all()))
    # permutations() is used instead of combinations() to ensure that the
    # result is irrespective of the ordering of the nodes:
    for results in permutations(self.result_static, 2):
      names         = [x[0] for x in results]
      nodes         = [db.session.query(Named).filter_by(name=x).one() for x in names]
      siblings      = [set(x[1]['next-siblings']) for x in results]
      siblings2     = map(lambda x:x[1].union(set([x[0]])), zip(names, siblings))
      union         = reduce(lambda l,r:l.union(r),        siblings)
      union2        = reduce(lambda l,r:l.union(r),        siblings2)
      intersection  = reduce(lambda l,r:l.intersection(r), siblings)
      intersection2 = reduce(lambda l,r:l.intersection(r), siblings2)
      self.assertEqual(union,
        set(map(
          lambda node:node.name,
          db.session.query(Named)
            .filter(Named.tree.filter_next_siblings_of_node(*nodes))
            .all())))
      self.assertEqual(union2,
        set(map(
          lambda node:node.name,
          db.session.query(Named)
            .filter(Named.tree.filter_next_siblings_of_node(*nodes, include_self=True))
            .all())))
      self.assertEqual(intersection,
        set(map(
          lambda node:node.name,
          db.session.query(Named)
            .filter(Named.tree.filter_next_siblings_of_node(*nodes, disjoint=False))
            .all())))
      self.assertEqual(intersection2,
        set(map(
          lambda node:node.name,
          db.session.query(Named)
            .filter(Named.tree.filter_next_siblings_of_node(*nodes, include_self=True, disjoint=False))
            .all())))
  def test_query_next_siblings_of_node(self):
    "Verify the siblings of each node against expected values"
    for pattern in self.result_static:
      name, result = pattern
      obj = db.session.query(Named).filter_by(name=name).one()
      self.assertEqual(result['next-siblings'],
        map(lambda x:x.name,
          Named.tree.query_next_siblings_of_node(obj)
            .order_by(Named.tree).all()))
      self.assertEqual([obj.name] + result['next-siblings'],
        map(lambda x:x.name,
          Named.tree.query_next_siblings_of_node(obj, include_self=True)
            .order_by(Named.tree).all()))
    # permutations() is used instead of combinations() to ensure that the
    # result is irrespective of the ordering of the nodes:
    for results in permutations(self.result_static, 2):
      names         = [x[0] for x in results]
      nodes         = [db.session.query(Named).filter_by(name=x).one() for x in names]
      siblings      = [set(x[1]['next-siblings']) for x in results]
      siblings2     = map(lambda x:x[1].union(set([x[0]])), zip(names, siblings))
      union         = reduce(lambda l,r:l.union(r),        siblings)
      union2        = reduce(lambda l,r:l.union(r),        siblings2)
      intersection  = reduce(lambda l,r:l.intersection(r), siblings)
      intersection2 = reduce(lambda l,r:l.intersection(r), siblings2)
      self.assertEqual(union,
        set(map(
          lambda node:node.name,
          Named.tree.query_next_siblings_of_node(*nodes)
            .all())))
      self.assertEqual(union2,
        set(map(
          lambda node:node.name,
          Named.tree.query_next_siblings_of_node(*nodes, include_self=True)
            .all())))
      self.assertEqual(intersection,
        set(map(
          lambda node:node.name,
          Named.tree.query_next_siblings_of_node(*nodes, disjoint=False)
            .all())))
      self.assertEqual(intersection2,
        set(map(
          lambda node:node.name,
          Named.tree.query_next_siblings_of_node(*nodes, include_self=True, disjoint=False)
            .all())))
  def test_filter_ancestors_of_node(self):
    "Verify the ancestors of each node against expected values"
    for pattern in self.result_static:
      name, result = pattern
      obj = db.session.query(Named).filter_by(name=name).one()
      self.assertEqual(result['ancestors'],
        map(lambda x:x.name,
          db.session.query(Named)
            .filter(Named.tree.filter_ancestors_of_node(obj))
            .order_by(Named.tree).all()))
      self.assertEqual(result['ancestors'] + [obj.name],
        map(lambda x:x.name,
          db.session.query(Named)
            .filter(Named.tree.filter_ancestors_of_node(obj, include_self=True))
            .order_by(Named.tree).all()))
    # permutations() is used instead of combinations() to ensure that the
    # result is irrespective of the ordering of the nodes:
    for results in permutations(self.result_static, 2):
      names         = [x[0] for x in results]
      nodes         = [db.session.query(Named).filter_by(name=x).one() for x in names]
      ancestors     = [set(x[1]['ancestors']) for x in results]
      ancestors2    = map(lambda x:x[1].union(set([x[0]])), zip(names, ancestors))
      union         = reduce(lambda l,r:l.union(r),        ancestors)
      union2        = reduce(lambda l,r:l.union(r),        ancestors2)
      intersection  = reduce(lambda l,r:l.intersection(r), ancestors)
      intersection2 = reduce(lambda l,r:l.intersection(r), ancestors2)
      self.assertEqual(union,
        set(map(
          lambda node:node.name,
          db.session.query(Named)
            .filter(Named.tree.filter_ancestors_of_node(*nodes))
            .all())))
      self.assertEqual(union2,
        set(map(
          lambda node:node.name,
          db.session.query(Named)
            .filter(Named.tree.filter_ancestors_of_node(*nodes, include_self=True))
            .all())))
      self.assertEqual(intersection,
        set(map(
          lambda node:node.name,
          db.session.query(Named)
            .filter(Named.tree.filter_ancestors_of_node(*nodes, disjoint=False))
            .all())))
      self.assertEqual(intersection2,
        set(map(
          lambda node:node.name,
          db.session.query(Named)
            .filter(Named.tree.filter_ancestors_of_node(*nodes, include_self=True, disjoint=False))
            .all())))
  def test_query_ancestors_of_node(self):
    "Verify the ancestors of each node against expected values"
    for pattern in self.result_static:
      name, result = pattern
      obj = db.session.query(Named).filter_by(name=name).one()
      self.assertEqual(result['ancestors'],
        map(lambda x:x.name,
          Named.tree.query_ancestors_of_node(obj)
            .order_by(Named.tree).all()))
      self.assertEqual(result['ancestors'] + [obj.name],
        map(lambda x:x.name,
          Named.tree.query_ancestors_of_node(obj, include_self=True)
            .order_by(Named.tree).all()))
    # permutations() is used instead of combinations() to ensure that the
    # result is irrespective of the ordering of the nodes:
    for results in permutations(self.result_static, 2):
      names         = [x[0] for x in results]
      nodes         = [db.session.query(Named).filter_by(name=x).one() for x in names]
      ancestors     = [set(x[1]['ancestors']) for x in results]
      ancestors2    = map(lambda x:x[1].union(set([x[0]])), zip(names, ancestors))
      union         = reduce(lambda l,r:l.union(r),        ancestors)
      union2        = reduce(lambda l,r:l.union(r),        ancestors2)
      intersection  = reduce(lambda l,r:l.intersection(r), ancestors)
      intersection2 = reduce(lambda l,r:l.intersection(r), ancestors2)
      self.assertEqual(union,
        set(map(
          lambda node:node.name,
          Named.tree.query_ancestors_of_node(*nodes)
            .all())))
      self.assertEqual(union2,
        set(map(
          lambda node:node.name,
          Named.tree.query_ancestors_of_node(*nodes, include_self=True)
            .all())))
      self.assertEqual(intersection,
        set(map(
          lambda node:node.name,
          Named.tree.query_ancestors_of_node(*nodes, disjoint=False)
            .all())))
      self.assertEqual(intersection2,
        set(map(
          lambda node:node.name,
          Named.tree.query_ancestors_of_node(*nodes, include_self=True, disjoint=False)
            .all())))
  def test_filter_children(self):
    "Verify the children of each node against expected values"
    for pattern in self.result_static:
      name, result = pattern
      obj = db.session.query(Named).filter_by(name=name).one()
      self.assertEqual(result['children'],
        map(lambda x:x.name,
          db.session.query(Named)
            .filter(obj.tree.filter_children())
            .order_by(Named.tree).all()))
  def test_query_children(self):
    "Verify the children of each node against expected values"
    for pattern in self.result_static:
      name, result = pattern
      obj = db.session.query(Named).filter_by(name=name).one()
      self.assertEqual(result['children'],
        map(lambda x:x.name,
            obj.tree.query_children().order_by(Named.tree).all()))
  def test_filter_children_of_node(self):
    "Verify the children of each node against expected values"
    for pattern in self.result_static:
      name, result = pattern
      obj = db.session.query(Named).filter_by(name=name).one()
      self.assertEqual(result['children'],
        map(lambda x:x.name,
          db.session.query(Named)
            .filter(Named.tree.filter_children_of_node(obj))
            .order_by(Named.tree).all()))
    # permutations() is used instead of combinations() to ensure that the
    # result is irrespective of the ordering of the nodes:
    for results in permutations(self.result_static, 2):
      names    = [x[0] for x in results]
      nodes    = [db.session.query(Named).filter_by(name=x).one() for x in names]
      children = [set(x[1]['children']) for x in results]
      union    = reduce(lambda l,r:l.union(r),        children)
      self.assertEqual(union,
        set(map(
          lambda node:node.name,
          db.session.query(Named)
            .filter(Named.tree.filter_children_of_node(*nodes))
            .all())))
  def test_query_children_of_node(self):
    "Verify the children of each node against expected values"
    for pattern in self.result_static:
      name, result = pattern
      obj = db.session.query(Named).filter_by(name=name).one()
      self.assertEqual(result['children'],
        map(lambda x:x.name,
          Named.tree.query_children_of_node(obj)
            .order_by(Named.tree).all()))
    # permutations() is used instead of combinations() to ensure that the
    # result is irrespective of the ordering of the nodes:
    for results in permutations(self.result_static, 2):
      names    = [x[0] for x in results]
      nodes    = [db.session.query(Named).filter_by(name=x).one() for x in names]
      children = [set(x[1]['children']) for x in results]
      union    = reduce(lambda l,r:l.union(r),        children)
      self.assertEqual(union,
        set(map(
          lambda node:node.name,
          Named.tree.query_children_of_node(*nodes)
            .all())))
  def test_filter_descendants(self):
    "Verify the descendants of each node against expected values"
    for pattern in self.result_static:
      name, result = pattern
      obj = db.session.query(Named).filter_by(name=name).one()
      self.assertEqual(result['descendants'],
        map(lambda x:x.name,
          db.session.query(Named)
            .filter(obj.tree.filter_descendants())
            .order_by(Named.tree).all()))
      self.assertEqual([obj.name] + result['descendants'],
        map(lambda x:x.name,
          db.session.query(Named)
            .filter(obj.tree.filter_descendants(include_self=True))
            .order_by(Named.tree).all()))
  def test_query_descendants(self):
    "Verify the descendants of each node against expected values"
    for pattern in self.result_static:
      name, result = pattern
      obj = db.session.query(Named).filter_by(name=name).one()
      self.assertEqual(result['descendants'],
        map(lambda x:x.name,
            obj.tree.query_descendants().order_by(Named.tree).all()))
      self.assertEqual([obj.name] + result['descendants'],
        map(lambda x:x.name,
            obj.tree.query_descendants(include_self=True).order_by(Named.tree).all()))
  def test_filter_descendants_of_node(self):
    "Verify the descendants of each node against expected values"
    for pattern in self.result_static:
      name, result = pattern
      obj = db.session.query(Named).filter_by(name=name).one()
      self.assertEqual(result['descendants'],
        map(lambda x:x.name,
          db.session.query(Named)
            .filter(Named.tree.filter_descendants_of_node(obj))
            .order_by(Named.tree).all()))
      self.assertEqual([obj.name] + result['descendants'],
        map(lambda x:x.name,
          db.session.query(Named)
            .filter(Named.tree.filter_descendants_of_node(obj, include_self=True))
            .order_by(Named.tree).all()))
    # permutations() is used instead of combinations() to ensure that the
    # result is irrespective of the ordering of the nodes:
    for results in permutations(self.result_static, 2):
      names         = [x[0] for x in results]
      nodes         = [db.session.query(Named).filter_by(name=x).one() for x in names]
      descendants   = [set(x[1]['descendants']) for x in results]
      descendants2  = map(lambda x:x[1].union(set([x[0]])), zip(names, descendants))
      union         = reduce(lambda l,r:l.union(r),        descendants)
      union2        = reduce(lambda l,r:l.union(r),        descendants2)
      intersection  = reduce(lambda l,r:l.intersection(r), descendants)
      intersection2 = reduce(lambda l,r:l.intersection(r), descendants2)
      self.assertEqual(union,
        set(map(
          lambda node:node.name,
          db.session.query(Named)
            .filter(Named.tree.filter_descendants_of_node(*nodes))
            .all())))
      self.assertEqual(union2,
        set(map(
          lambda node:node.name,
          db.session.query(Named)
            .filter(Named.tree.filter_descendants_of_node(*nodes, include_self=True))
            .all())))
      self.assertEqual(intersection,
        set(map(
          lambda node:node.name,
          db.session.query(Named)
            .filter(Named.tree.filter_descendants_of_node(*nodes, disjoint=False))
            .all())))
      self.assertEqual(intersection2,
        set(map(
          lambda node:node.name,
          db.session.query(Named)
            .filter(Named.tree.filter_descendants_of_node(*nodes, include_self=True, disjoint=False))
            .all())))
  def test_query_descendants_of_node(self):
    "Verify the descendants of each node against expected values"
    for pattern in self.result_static:
      name, result = pattern
      obj = db.session.query(Named).filter_by(name=name).one()
      self.assertEqual(result['descendants'],
        map(lambda x:x.name,
          Named.tree.query_descendants_of_node(obj)
            .order_by(Named.tree).all()))
      self.assertEqual([obj.name] + result['descendants'],
        map(lambda x:x.name,
          Named.tree.query_descendants_of_node(obj, include_self=True)
            .order_by(Named.tree).all()))
    # permutations() is used instead of combinations() to ensure that the
    # result is irrespective of the ordering of the nodes:
    for results in permutations(self.result_static, 2):
      names         = [x[0] for x in results]
      nodes         = [db.session.query(Named).filter_by(name=x).one() for x in names]
      descendants   = [set(x[1]['descendants']) for x in results]
      descendants2  = map(lambda x:x[1].union(set([x[0]])), zip(names, descendants))
      union         = reduce(lambda l,r:l.union(r),        descendants)
      union2        = reduce(lambda l,r:l.union(r),        descendants2)
      intersection  = reduce(lambda l,r:l.intersection(r), descendants)
      intersection2 = reduce(lambda l,r:l.intersection(r), descendants2)
      self.assertEqual(union,
        set(map(
          lambda node:node.name,
          Named.tree.query_descendants_of_node(*nodes)
            .all())))
      self.assertEqual(union2,
        set(map(
          lambda node:node.name,
          Named.tree.query_descendants_of_node(*nodes, include_self=True)
            .all())))
      self.assertEqual(intersection,
        set(map(
          lambda node:node.name,
          Named.tree.query_descendants_of_node(*nodes, disjoint=False)
            .all())))
      self.assertEqual(intersection2,
        set(map(
          lambda node:node.name,
          Named.tree.query_descendants_of_node(*nodes, include_self=True, disjoint=False)
            .all())))
  def get_descendant_count(self):
    "Verify the number of descendants of each node against the expected count"
    for pattern in self.result_static:
      name, result = pattern
      obj = db.session.query(Named).filter_by(name=name).one()
      self.assertEqual(len(result['descendants']), obj.tree.get_descendant_count())
  def test_filter_leaf_nodes(self):
    "Verify the leaf nodes of each node against expected values"
    for pattern in self.result_static:
      name, result = pattern
      obj = db.session.query(Named).filter_by(name=name).one()
      self.assertEqual(result['leaf-nodes'],
        map(lambda x:x.name,
          db.session.query(Named)
            .filter(obj.tree.filter_leaf_nodes())
            .order_by(Named.tree).all()))
      if result['descendants']:
        expected = []
      else:
        expected = [obj.name]
      self.assertEqual(expected + result['leaf-nodes'],
        map(lambda x:x.name,
          db.session.query(Named)
            .filter(obj.tree.filter_leaf_nodes(include_self=True))
            .order_by(Named.tree).all()))
    expected = set(map(
      lambda x: x[0],
      filter(lambda x: not x[1]['descendants'], self.result_static)))
    self.assertEqual(expected,
      set(map(
        lambda node:node.name,
        db.session.query(Named)
          .filter(Named.tree.filter_leaf_nodes()).all())))
  def test_query_leaf_nodes(self):
    "Verify the leaf nodes of each node against expected values"
    for pattern in self.result_static:
      name, result = pattern
      obj = db.session.query(Named).filter_by(name=name).one()
      self.assertEqual(result['leaf-nodes'],
        map(lambda x:x.name,
            obj.tree.query_leaf_nodes().order_by(Named.tree).all()))
      if result['descendants']:
        expected = []
      else:
        expected = [obj.name]
      self.assertEqual(expected + result['leaf-nodes'],
        map(lambda x:x.name,
            obj.tree.query_leaf_nodes(include_self=True).order_by(Named.tree).all()))
    expected = set(map(
      lambda x: x[0],
      filter(lambda x: not x[1]['descendants'], self.result_static)))
    self.assertEqual(expected,
      set(map(
        lambda node:node.name,
        Named.tree.query_leaf_nodes(session=db.session).all())))
  def test_filter_leaf_nodes_by_tree_id(self):
    "Verify the leaf nodes of each node against expected values"
    for pattern in self.name_pattern:
      name, params, children = pattern
      expected = set(map(
        lambda x:x[1]['leaf-nodes'] or [x[0]],
        filter(lambda x:x[0] == name, self.result_static))[0])
      self.assertEqual(expected, set(map(
        lambda node:node.name,
        db.session.query(Named)
          .filter(Named.tree.filter_leaf_nodes_by_tree_id(params['id']))
          .all())))
  def test_query_leaf_nodes_by_tree_id(self):
    "Verify the leaf nodes of each node against expected values"
    for pattern in self.name_pattern:
      name, params, children = pattern
      expected = set(map(
        lambda x:x[1]['leaf-nodes'] or [x[0]],
        filter(lambda x:x[0] == name, self.result_static))[0])
      self.assertEqual(expected, set(map(
        lambda node:node.name,
        Named.tree.query_leaf_nodes_by_tree_id(params['id'], session=db.session).all())))
  def test_filter_leaf_nodes_of_node(self):
    "Verify the leaf nodes of each node against expected values"
    for pattern in self.result_static:
      name, result = pattern
      obj = db.session.query(Named).filter_by(name=name).one()
      self.assertEqual(result['leaf-nodes'],
        map(lambda x:x.name,
          db.session.query(Named)
            .filter(Named.tree.filter_leaf_nodes_of_node(obj))
            .order_by(Named.tree).all()))
      self.assertEqual(result['leaf-nodes'] or [obj.name],
        map(lambda x:x.name,
          db.session.query(Named)
            .filter(Named.tree.filter_leaf_nodes_of_node(obj, include_self=True))
            .order_by(Named.tree).all()))
    # permutations() is used instead of combinations() to ensure that the
    # result is irrespective of the ordering of the nodes:
    for results in permutations(self.result_static, 2):
      names         = [x[0] for x in results]
      nodes         = [db.session.query(Named).filter_by(name=x).one() for x in names]
      leaf_nodes    = [set(x[1]['leaf-nodes']) for x in results]
      leaf_nodes2   = map(lambda x:x[1] or set([x[0]]), zip(names, leaf_nodes))
      union         = reduce(lambda l,r:l.union(r),        leaf_nodes)
      union2        = reduce(lambda l,r:l.union(r),        leaf_nodes2)
      intersection  = reduce(lambda l,r:l.intersection(r), leaf_nodes)
      intersection2 = reduce(lambda l,r:l.intersection(r), leaf_nodes2)
      self.assertEqual(union,
        set(map(
          lambda node:node.name,
          db.session.query(Named)
            .filter(Named.tree.filter_leaf_nodes_of_node(*nodes))
            .all())))
      self.assertEqual(union2,
        set(map(
          lambda node:node.name,
          db.session.query(Named)
            .filter(Named.tree.filter_leaf_nodes_of_node(*nodes, include_self=True))
            .all())))
      self.assertEqual(intersection,
        set(map(
          lambda node:node.name,
          db.session.query(Named)
            .filter(Named.tree.filter_leaf_nodes_of_node(*nodes, disjoint=False))
            .all())))
      self.assertEqual(intersection2,
        set(map(
          lambda node:node.name,
          db.session.query(Named)
            .filter(Named.tree.filter_leaf_nodes_of_node(*nodes, include_self=True, disjoint=False))
            .all())))
  def test_query_leaf_nodes_of_node(self):
    "Verify the leaf nodes of each node against expected values"
    for pattern in self.result_static:
      name, result = pattern
      obj = db.session.query(Named).filter_by(name=name).one()
      self.assertEqual(result['leaf-nodes'],
        map(lambda x:x.name,
          Named.tree.query_leaf_nodes_of_node(obj)
            .order_by(Named.tree).all()))
      self.assertEqual(result['leaf-nodes'] or [obj.name],
        map(lambda x:x.name,
          Named.tree.query_leaf_nodes_of_node(obj, include_self=True)
            .order_by(Named.tree).all()))
    # permutations() is used instead of combinations() to ensure that the
    # result is irrespective of the ordering of the nodes:
    for results in permutations(self.result_static, 2):
      names         = [x[0] for x in results]
      nodes         = [db.session.query(Named).filter_by(name=x).one() for x in names]
      leaf_nodes    = [set(x[1]['leaf-nodes']) for x in results]
      leaf_nodes2   = map(lambda x:x[1] or set([x[0]]), zip(names, leaf_nodes))
      union         = reduce(lambda l,r:l.union(r),        leaf_nodes)
      union2        = reduce(lambda l,r:l.union(r),        leaf_nodes2)
      intersection  = reduce(lambda l,r:l.intersection(r), leaf_nodes)
      intersection2 = reduce(lambda l,r:l.intersection(r), leaf_nodes2)
      self.assertEqual(union,
        set(map(
          lambda node:node.name,
          Named.tree.query_leaf_nodes_of_node(*nodes)
            .all())))
      self.assertEqual(union2,
        set(map(
          lambda node:node.name,
          Named.tree.query_leaf_nodes_of_node(*nodes, include_self=True)
            .all())))
      self.assertEqual(intersection,
        set(map(
          lambda node:node.name,
          Named.tree.query_leaf_nodes_of_node(*nodes, disjoint=False)
            .all())))
      self.assertEqual(intersection2,
        set(map(
          lambda node:node.name,
          Named.tree.query_leaf_nodes_of_node(*nodes, include_self=True, disjoint=False)
            .all())))
  def test_is_root_node(self):
    for pattern in self.result_static:
      name, result = pattern
      obj = db.session.query(Named).filter_by(name=name).one()
      self.assertEqual(not bool(result['parent']), obj.tree.is_root_node)
  def test_is_child_node(self):
    for pattern in self.result_static:
      name, result = pattern
      obj = db.session.query(Named).filter_by(name=name).one()
      self.assertEqual(bool(result['parent']), obj.tree.is_child_node)
  def test_is_leaf_node(self):
    for pattern in self.result_static:
      name, result = pattern
      obj = db.session.query(Named).filter_by(name=name).one()
      self.assertEqual(not bool(result['children']), obj.tree.is_leaf_node)
  def test_is_ancestor_of(self):
    for results in permutations(self.result_static, 2):
      names = [x[0] for x in results]
      nodes = [db.session.query(Named).filter_by(name=x).one() for x in names]
      self.assertEqual(
        names[0] in results[1][1]['ancestors'],
        nodes[0].tree.is_ancestor_of(nodes[1]))
      self.assertEqual(
        names[0] in results[1][1]['ancestors'] or names[0] == names[1],
        nodes[0].tree.is_ancestor_of(nodes[1], include_self=True))
  def test_is_sibling_of(self):
    for results in permutations(self.result_static, 2):
      names = [x[0] for x in results]
      nodes = [db.session.query(Named).filter_by(name=x).one() for x in names]
      self.assertEqual(
        names[0] in results[1][1]['previous-siblings'] or
        names[0] in results[1][1]['next-siblings'],
        nodes[0].tree.is_sibling_of(nodes[1]))
      self.assertEqual(
        names[0] in results[1][1]['previous-siblings'] or
        names[0] in results[1][1]['next-siblings']     or
        names[0] == names[1],
        nodes[0].tree.is_sibling_of(nodes[1], include_self=True))
  def test_is_child_of(self):
    for results in permutations(self.result_static, 2):
      names = [x[0] for x in results]
      nodes = [db.session.query(Named).filter_by(name=x).one() for x in names]
      self.assertEqual(
        names[0] in results[1][1]['children'],
        nodes[0].tree.is_child_of(nodes[1]))
  def test_is_descendant_of(self):
    for results in permutations(self.result_static, 2):
      names = [x[0] for x in results]
      nodes = [db.session.query(Named).filter_by(name=x).one() for x in names]
      self.assertEqual(
        names[0] in results[1][1]['descendants'],
        nodes[0].tree.is_descendant_of(nodes[1]))
      self.assertEqual(
        names[0] in results[1][1]['descendants'] or names[0] == names[1],
        nodes[0].tree.is_descendant_of(nodes[1], include_self=True))
  def test_are_root_nodes(self):
    for results in permutations(self.result_static, 2):
      names = [x[0] for x in results]
      nodes = [db.session.query(Named).filter_by(name=x).one() for x in names]
      self.assertEqual(
        results[0][1]['parent'] == [] or
        results[1][1]['parent'] == [],
        Named.tree.any_root_nodes(*nodes))
      self.assertEqual(
        results[0][1]['parent'] == [] and
        results[1][1]['parent'] == [],
        Named.tree.all_root_nodes(*nodes))
  def test_are_child_nodes(self):
    for results in permutations(self.result_static, 2):
      names = [x[0] for x in results]
      nodes = [db.session.query(Named).filter_by(name=x).one() for x in names]
      self.assertEqual(
        bool(results[0][1]['parent']) or
        bool(results[1][1]['parent']),
        Named.tree.any_child_nodes(*nodes))
      self.assertEqual(
        bool(results[0][1]['parent']) and
        bool(results[1][1]['parent']),
        Named.tree.all_child_nodes(*nodes))
  def test_are_leaf_nodes(self):
    for results in permutations(self.result_static, 2):
      names = [x[0] for x in results]
      nodes = [db.session.query(Named).filter_by(name=x).one() for x in names]
      self.assertEqual(
        results[0][1]['children'] == [] or
        results[1][1]['children'] == [],
        Named.tree.any_leaf_nodes(*nodes))
      self.assertEqual(
        results[0][1]['children'] == [] and
        results[1][1]['children'] == [],
        Named.tree.all_leaf_nodes(*nodes))
  def test_ancestors_of(self):
    for results in permutations(self.result_static, 3):
      names = [x[0] for x in results]
      nodes = [db.session.query(Named).filter_by(name=x).one() for x in names]
      ancestors  = results[0][1]['ancestors']
      ancestors2 = results[0][1]['ancestors'] + names[:1]
      self.assertEqual(
        names[1] in ancestors or names[2] in ancestors,
        Named.tree.any_ancestors_of(*nodes))
      self.assertEqual(
        names[1] in ancestors2 or names[2] in ancestors2,
        Named.tree.any_ancestors_of(*nodes, include_self=True))
      self.assertEqual(
        names[1] in ancestors and names[2] in ancestors,
        Named.tree.all_ancestors_of(*nodes))
      self.assertEqual(
        names[1] in ancestors2 and names[2] in ancestors2,
        Named.tree.all_ancestors_of(*nodes, include_self=True))
  def test_siblings_of(self):
    for results in permutations(self.result_static, 3):
      names     = [x[0] for x in results]
      nodes     = [db.session.query(Named).filter_by(name=x).one() for x in names]
      siblings  = results[0][1]['previous-siblings'] + results[0][1]['next-siblings']
      siblings2 = results[0][1]['previous-siblings'] + names[:1] + results[0][1]['next-siblings']
      self.assertEqual(
        names[1] in siblings or names[2] in siblings,
        Named.tree.any_siblings_of(*nodes))
      self.assertEqual(
        names[1] in siblings2 or names[2] in siblings2,
        Named.tree.any_siblings_of(*nodes, include_self=True))
      self.assertEqual(
        names[1] in siblings and names[2] in siblings,
        Named.tree.all_siblings_of(*nodes))
      self.assertEqual(
        names[1] in siblings2 and names[2] in siblings2,
        Named.tree.all_siblings_of(*nodes, include_self=True))
  def test_children_of(self):
    for results in permutations(self.result_static, 3):
      names    = [x[0] for x in results]
      nodes    = [db.session.query(Named).filter_by(name=x).one() for x in names]
      children = results[0][1]['children']
      self.assertEqual(
        names[1] in children or names[2] in children,
        Named.tree.any_children_of(*nodes))
      self.assertEqual(
        names[1] in children and names[2] in children,
        Named.tree.all_children_of(*nodes))
  def test_descendants_of(self):
    for results in permutations(self.result_static, 3):
      names = [x[0] for x in results]
      nodes = [db.session.query(Named).filter_by(name=x).one() for x in names]
      descendants  = results[0][1]['descendants']
      descendants2 = names[:1] + results[0][1]['descendants']
      self.assertEqual(
        names[1] in descendants or names[2] in descendants,
        Named.tree.any_descendants_of(*nodes))
      self.assertEqual(
        names[1] in descendants2 or names[2] in descendants2,
        Named.tree.any_descendants_of(*nodes, include_self=True))
      self.assertEqual(
        names[1] in descendants and names[2] in descendants,
        Named.tree.all_descendants_of(*nodes))
      self.assertEqual(
        names[1] in descendants2 and names[2] in descendants2,
        Named.tree.all_descendants_of(*nodes, include_self=True))

# ===----------------------------------------------------------------------===


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(NamedTestCase))
    return suite
