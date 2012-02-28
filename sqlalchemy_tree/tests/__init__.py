#!/usr/bin/env python
# -*- coding: utf-8 -*-

# === sqlalchemy_tree.tests -----------------------------------------------===
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

# Python standard library, unit testing
from unittest2 import TestCase

# Python standard library, combinatoric generators
from itertools import permutations

# SQLAlchemy object-relational mapper
import sqlalchemy
from sqlalchemy import *
from sqlalchemy.orm import mapper, relationship, backref, sessionmaker

# SQLAlchemy tree extension
import sqlalchemy_tree
from sqlalchemy_tree import *

# ===----------------------------------------------------------------------===

class _Database(object):
  def __init__(self):
    self.engine   = create_engine('sqlite:///:memory:')
    self.metadata = MetaData(self.engine)
    self.Session  = sessionmaker(bind=self.engine)
db = _Database()

# ===----------------------------------------------------------------------===

class Named(object):
  def __init__(self, *args, **kwargs):
    name   = kwargs.pop('name',   None)
    parent = kwargs.pop('parent', None)
    super(Named, self).__init__(*args, **kwargs)
    self.name   = name
    self.parent = parent
  def __unicode__(self):
    return self.name
named = Table('sqlalchemy_tree__tests__named', db.metadata,
  # Primary-key:
  Column('id', Integer,
    Sequence('sqlalchemy_tree__tests__named__id_seq'),
    primary_key = True),
  # Unicode identifier:
  Column('name', Unicode,
    nullable = False,
    unique   = True),
  # Adjacency-list link:
  Column('parent_id', Integer,
    ForeignKey('sqlalchemy_tree__tests__named.id')),
)
Named.tree = TreeManager(named)
mapper(Named, named, properties={
  'parent': relationship(Named,
    backref     = backref('children', lazy='dynamic'),
    remote_side = named.c.id),
})
Named.tree.register()

# ===----------------------------------------------------------------------===

def get_tree_details():
  ""
  options = Named.tree._tree_options
  def _get_subtree(parent):
    if parent is None:
      children = db.session.query(Named) \
                           .filter(Named.tree.filter_root_nodes()) \
                           .order_by(options.tree_id_field) \
                           .all()
    else:
      children = db.session.query(Named) \
                           .filter(parent.tree.filter_children()) \
                           .order_by(options.left_field) \
                           .all()
    return [(n.name, {'id':   getattr(n, options.tree_id_field.name),
                      'left': getattr(n, options.left_field.name),
                      'right':getattr(n, options.right_field.name),
                      'depth':getattr(n, options.depth_field.name)},
             _get_subtree(n))
            for n in children]
  return _get_subtree(None)

class TreeTestMixin(object):
  "Provides a framework for testing tree structures using the `named` table."
  def _fill_tree(self):
    def _create_node(name, fields, parent=None):
      node = Named(name=name)
      Named.tree.insert(node, parent)
      db.session.add(node)
      db.session.commit()
      return node
    def _process_node(pattern, parent=None):
      name, fields, children = pattern
      node = _create_node(name, fields, parent)
      for child in children:
        _process_node(child, node)
    for root in self.name_pattern:
      _process_node(root)
    db.session.commit()
  def setUp(self):
    # Enable long-format diffs, which are necessary due to the large size of
    # the assert comparisons we do.
    self.maxDiff = None
    db.metadata.drop_all()
    db.metadata.create_all()
    db.session = db.Session()
    self._fill_tree()
  def tearDown(self):
    db.session.close()
  def test_fill_tree(self):
    "Fill the database with ‘_fill_tree()’, and double-check the result"
    def _check_node(pattern):
      name, fields, children = pattern
      node = db.session.query(Named).filter(named.c.name==name).one()
      for field in fields.keys():
        self.assertEqual(fields[field], getattr(node, 'tree_'+field))
      for child in children:
        _check_node(child)
    for root in self.name_pattern:
      _check_node(root)

# ===----------------------------------------------------------------------===

class NamedTestCase(TreeTestMixin, TestCase):
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
      'next-siblings': ['root2','root3'],
      'children': ['child11','child12','child13'],
      'descendants': ['child11','child12','child13'],
      'leaf-nodes': ['child11','child12','child13']}),
    (u"child11", {
      'ancestors': ['root1'],
      'parent': ['root1'],
      'previous-siblings': [],
      'next-siblings': ['child12', 'child13'],
      'children': [],
      'descendants': [],
      'leaf-nodes': []}),
    (u"child12", {
      'ancestors': ['root1'],
      'parent': ['root1'],
      'previous-siblings': ['child11'],
      'next-siblings': ['child13'],
      'children': [],
      'descendants': [],
      'leaf-nodes': []}),
    (u"child13", {
      'ancestors': ['root1'],
      'parent': ['root1'],
      'previous-siblings': ['child11','child12'],
      'next-siblings': [],
      'children': [],
      'descendants': [],
      'leaf-nodes': []}),
    (u"root2", {
      'ancestors': [],
      'parent': [],
      'previous-siblings': ['root1'],
      'next-siblings': ['root3'],
      'children': ['child21','child22','child23'],
      'descendants': [
        'child21','child211','child212','child2121','child2122','child21221',
        'child21222','child22','child23'],
      'leaf-nodes': ['child211','child2121','child21221','child21222',
        'child22','child23']}),
    (u"child21", {
      'ancestors': ['root2'],
      'parent': ['root2'],
      'previous-siblings': [],
      'next-siblings': ['child22','child23'],
      'children': ['child211','child212'],
      'descendants': [
        'child211','child212','child2121','child2122','child21221',
        'child21222'],
      'leaf-nodes': ['child211','child2121','child21221','child21222']}),
    (u"child211", {
      'ancestors': ['root2','child21'],
      'parent': ['child21'],
      'previous-siblings': [],
      'next-siblings': ['child212'],
      'children': [],
      'descendants': [],
      'leaf-nodes': []}),
    (u"child212", {
      'ancestors': ['root2','child21'],
      'parent': ['child21'],
      'previous-siblings': ['child211'],
      'next-siblings': [],
      'children': ['child2121','child2122'],
      'descendants': ['child2121','child2122','child21221','child21222'],
      'leaf-nodes': ['child2121','child21221','child21222']}),
    (u"child2121", {
      'ancestors': ['root2','child21','child212'],
      'parent': ['child212'],
      'previous-siblings': [],
      'next-siblings': ['child2122'],
      'children': [],
      'descendants': [],
      'leaf-nodes': []}),
    (u"child2122", {
      'ancestors': ['root2','child21','child212'],
      'parent': ['child212'],
      'previous-siblings': ['child2121'],
      'next-siblings': [],
      'children': ['child21221','child21222'],
      'descendants': ['child21221','child21222'],
      'leaf-nodes': ['child21221','child21222']}),
    (u"child21221", {
      'ancestors': ['root2','child21','child212','child2122'],
      'parent': ['child2122'],
      'previous-siblings': [],
      'next-siblings': ['child21222'],
      'children': [],
      'descendants': [],
      'leaf-nodes': []}),
    (u"child21222", {
      'ancestors': ['root2','child21','child212','child2122'],
      'parent': ['child2122'],
      'previous-siblings': ['child21221'],
      'next-siblings': [],
      'children': [],
      'descendants': [],
      'leaf-nodes': []}),
    (u"child22", {
      'ancestors': ['root2'],
      'parent': ['root2'],
      'previous-siblings': ['child21'],
      'next-siblings': ['child23'],
      'children': [],
      'descendants': [],
      'leaf-nodes': []}),
    (u"child23", {
      'ancestors': ['root2'],
      'parent': ['root2'],
      'previous-siblings': ['child21','child22'],
      'next-siblings': [],
      'children': [],
      'descendants': [],
      'leaf-nodes': []}),
    (u"root3", {
      'ancestors': [],
      'parent': [],
      'previous-siblings': ['root1','root2'],
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

class DeletionTestCase(NamedTestCase):
  def _delete_helper(self, name, result):
    node = db.session.query(Named).filter_by(name=name).one()
    db.session.delete(node)
    db.session.commit()
    self.assertEqual(get_tree_details(), result)
  def test_del_root1(self):
    name = u"root1"
    result = [
      (u"child11", {'id':1, 'left':1, 'right':2, 'depth':0}, []),
      (u"child12", {'id':2, 'left':1, 'right':2, 'depth':0}, []),
      (u"child13", {'id':3, 'left':1, 'right':2, 'depth':0}, []),
      (u"root2", {'id':4, 'left':1, 'right':20, 'depth':0}, [
        (u"child21", {'id':4, 'left':2, 'right':15, 'depth':1}, [
          (u"child211", {'id':4, 'left':3, 'right':4, 'depth':2}, []),
          (u"child212", {'id':4, 'left':5, 'right':14, 'depth':2}, [
            (u"child2121", {'id':4, 'left':6, 'right':7, 'depth':3}, []),
            (u"child2122", {'id':4, 'left':8, 'right':13, 'depth':3}, [
              (u"child21221", {'id':4, 'left':9, 'right':10, 'depth':4}, []),
              (u"child21222", {'id':4, 'left':11, 'right':12, 'depth':4}, []),
            ]),
          ]),
        ]),
        (u"child22", {'id':4, 'left':16, 'right':17, 'depth':1}, []),
        (u"child23", {'id':4, 'left':18, 'right':19, 'depth':1}, []),
      ]),
      (u"root3", {'id':5, 'left':1, 'right':2, 'depth':0}, []),
    ]
    self._delete_helper(name, result)
  def test_del_child11(self):
    name = u"child11"
    result = [
      (u"root1", {'id':1, 'left':1, 'right':6, 'depth':0}, [
        (u"child12", {'id':1, 'left':2, 'right':3, 'depth':1}, []),
        (u"child13", {'id':1, 'left':4, 'right':5, 'depth':1}, []),
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
    self._delete_helper(name, result)
  def test_del_child12(self):
    name = u"child12"
    result = [
      (u"root1", {'id':1, 'left':1, 'right':6, 'depth':0}, [
        (u"child11", {'id':1, 'left':2, 'right':3, 'depth':1}, []),
        (u"child13", {'id':1, 'left':4, 'right':5, 'depth':1}, []),
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
    self._delete_helper(name, result)
  def test_del_child13(self):
    name = u"child13"
    result = [
      (u"root1", {'id':1, 'left':1, 'right':6, 'depth':0}, [
        (u"child11", {'id':1, 'left':2, 'right':3, 'depth':1}, []),
        (u"child12", {'id':1, 'left':4, 'right':5, 'depth':1}, []),
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
    self._delete_helper(name, result)
  def test_del_root2(self):
    name = u"root2"
    result = [
      (u"root1", {'id':1, 'left':1, 'right':8, 'depth':0}, [
        (u"child11", {'id':1, 'left':2, 'right':3, 'depth':1}, []),
        (u"child12", {'id':1, 'left':4, 'right':5, 'depth':1}, []),
        (u"child13", {'id':1, 'left':6, 'right':7, 'depth':1}, []),
      ]),
      (u"child21", {'id':2, 'left':1, 'right':14, 'depth':0}, [
        (u"child211", {'id':2, 'left':2, 'right':3, 'depth':1}, []),
        (u"child212", {'id':2, 'left':4, 'right':13, 'depth':1}, [
          (u"child2121", {'id':2, 'left':5, 'right':6, 'depth':2}, []),
          (u"child2122", {'id':2, 'left':7, 'right':12, 'depth':2}, [
            (u"child21221", {'id':2, 'left':8, 'right':9, 'depth':3}, []),
            (u"child21222", {'id':2, 'left':10, 'right':11, 'depth':3}, []),
          ]),
        ]),
      ]),
      (u"child22", {'id':3, 'left':1, 'right':2, 'depth':0}, []),
      (u"child23", {'id':4, 'left':1, 'right':2, 'depth':0}, []),
      (u"root3", {'id':5, 'left':1, 'right':2, 'depth':0}, []),
    ]
    self._delete_helper(name, result)
  def test_del_child21(self):
    name = u"child21"
    result = [
      (u"root1", {'id':1, 'left':1, 'right':8, 'depth':0}, [
        (u"child11", {'id':1, 'left':2, 'right':3, 'depth':1}, []),
        (u"child12", {'id':1, 'left':4, 'right':5, 'depth':1}, []),
        (u"child13", {'id':1, 'left':6, 'right':7, 'depth':1}, []),
      ]),
      (u"root2", {'id':2, 'left':1, 'right':18, 'depth':0}, [
        (u"child211", {'id':2, 'left':2, 'right':3, 'depth':1}, []),
        (u"child212", {'id':2, 'left':4, 'right':13, 'depth':1}, [
          (u"child2121", {'id':2, 'left':5, 'right':6, 'depth':2}, []),
          (u"child2122", {'id':2, 'left':7, 'right':12, 'depth':2}, [
            (u"child21221", {'id':2, 'left':8, 'right':9, 'depth':3}, []),
            (u"child21222", {'id':2, 'left':10, 'right':11, 'depth':3}, []),
          ]),
        ]),
        (u"child22", {'id':2, 'left':14, 'right':15, 'depth':1}, []),
        (u"child23", {'id':2, 'left':16, 'right':17, 'depth':1}, []),
      ]),
      (u"root3", {'id':3, 'left':1, 'right':2, 'depth':0}, []),
    ]
    self._delete_helper(name, result)
  def test_del_child211(self):
    name = u"child211"
    result = [
      (u"root1", {'id':1, 'left':1, 'right':8, 'depth':0}, [
        (u"child11", {'id':1, 'left':2, 'right':3, 'depth':1}, []),
        (u"child12", {'id':1, 'left':4, 'right':5, 'depth':1}, []),
        (u"child13", {'id':1, 'left':6, 'right':7, 'depth':1}, []),
      ]),
      (u"root2", {'id':2, 'left':1, 'right':18, 'depth':0}, [
        (u"child21", {'id':2, 'left':2, 'right':13, 'depth':1}, [
          (u"child212", {'id':2, 'left':3, 'right':12, 'depth':2}, [
            (u"child2121", {'id':2, 'left':4, 'right':5, 'depth':3}, []),
            (u"child2122", {'id':2, 'left':6, 'right':11, 'depth':3}, [
              (u"child21221", {'id':2, 'left':7, 'right':8, 'depth':4}, []),
              (u"child21222", {'id':2, 'left':9, 'right':10, 'depth':4}, []),
            ]),
          ]),
        ]),
        (u"child22", {'id':2, 'left':14, 'right':15, 'depth':1}, []),
        (u"child23", {'id':2, 'left':16, 'right':17, 'depth':1}, []),
      ]),
      (u"root3", {'id':3, 'left':1, 'right':2, 'depth':0}, []),
    ]
    self._delete_helper(name, result)
  def test_del_child212(self):
    name = u"child212"
    result = [
      (u"root1", {'id':1, 'left':1, 'right':8, 'depth':0}, [
        (u"child11", {'id':1, 'left':2, 'right':3, 'depth':1}, []),
        (u"child12", {'id':1, 'left':4, 'right':5, 'depth':1}, []),
        (u"child13", {'id':1, 'left':6, 'right':7, 'depth':1}, []),
      ]),
      (u"root2", {'id':2, 'left':1, 'right':18, 'depth':0}, [
        (u"child21", {'id':2, 'left':2, 'right':13, 'depth':1}, [
          (u"child211", {'id':2, 'left':3, 'right':4, 'depth':2}, []),
          (u"child2121", {'id':2, 'left':5, 'right':6, 'depth':2}, []),
          (u"child2122", {'id':2, 'left':7, 'right':12, 'depth':2}, [
            (u"child21221", {'id':2, 'left':8, 'right':9, 'depth':3}, []),
            (u"child21222", {'id':2, 'left':10, 'right':11, 'depth':3}, []),
          ]),
        ]),
        (u"child22", {'id':2, 'left':14, 'right':15, 'depth':1}, []),
        (u"child23", {'id':2, 'left':16, 'right':17, 'depth':1}, []),
      ]),
      (u"root3", {'id':3, 'left':1, 'right':2, 'depth':0}, []),
    ]
    self._delete_helper(name, result)
  def test_del_child2121(self):
    name = u"child2121"
    result = [
      (u"root1", {'id':1, 'left':1, 'right':8, 'depth':0}, [
        (u"child11", {'id':1, 'left':2, 'right':3, 'depth':1}, []),
        (u"child12", {'id':1, 'left':4, 'right':5, 'depth':1}, []),
        (u"child13", {'id':1, 'left':6, 'right':7, 'depth':1}, []),
      ]),
      (u"root2", {'id':2, 'left':1, 'right':18, 'depth':0}, [
        (u"child21", {'id':2, 'left':2, 'right':13, 'depth':1}, [
          (u"child211", {'id':2, 'left':3, 'right':4, 'depth':2}, []),
          (u"child212", {'id':2, 'left':5, 'right':12, 'depth':2}, [
            (u"child2122", {'id':2, 'left':6, 'right':11, 'depth':3}, [
              (u"child21221", {'id':2, 'left':7, 'right':8, 'depth':4}, []),
              (u"child21222", {'id':2, 'left':9, 'right':10, 'depth':4}, []),
            ]),
          ]),
        ]),
        (u"child22", {'id':2, 'left':14, 'right':15, 'depth':1}, []),
        (u"child23", {'id':2, 'left':16, 'right':17, 'depth':1}, []),
      ]),
      (u"root3", {'id':3, 'left':1, 'right':2, 'depth':0}, []),
    ]
    self._delete_helper(name, result)
  def test_del_child2122(self):
    name = u"child2122"
    result = [
      (u"root1", {'id':1, 'left':1, 'right':8, 'depth':0}, [
        (u"child11", {'id':1, 'left':2, 'right':3, 'depth':1}, []),
        (u"child12", {'id':1, 'left':4, 'right':5, 'depth':1}, []),
        (u"child13", {'id':1, 'left':6, 'right':7, 'depth':1}, []),
      ]),
      (u"root2", {'id':2, 'left':1, 'right':18, 'depth':0}, [
        (u"child21", {'id':2, 'left':2, 'right':13, 'depth':1}, [
          (u"child211", {'id':2, 'left':3, 'right':4, 'depth':2}, []),
          (u"child212", {'id':2, 'left':5, 'right':12, 'depth':2}, [
            (u"child2121", {'id':2, 'left':6, 'right':7, 'depth':3}, []),
            (u"child21221", {'id':2, 'left':8, 'right':9, 'depth':3}, []),
            (u"child21222", {'id':2, 'left':10, 'right':11, 'depth':3}, []),
          ]),
        ]),
        (u"child22", {'id':2, 'left':14, 'right':15, 'depth':1}, []),
        (u"child23", {'id':2, 'left':16, 'right':17, 'depth':1}, []),
      ]),
      (u"root3", {'id':3, 'left':1, 'right':2, 'depth':0}, []),
    ]
    self._delete_helper(name, result)
  def test_del_child21221(self):
    name = u"child21221"
    result = [
      (u"root1", {'id':1, 'left':1, 'right':8, 'depth':0}, [
        (u"child11", {'id':1, 'left':2, 'right':3, 'depth':1}, []),
        (u"child12", {'id':1, 'left':4, 'right':5, 'depth':1}, []),
        (u"child13", {'id':1, 'left':6, 'right':7, 'depth':1}, []),
      ]),
      (u"root2", {'id':2, 'left':1, 'right':18, 'depth':0}, [
        (u"child21", {'id':2, 'left':2, 'right':13, 'depth':1}, [
          (u"child211", {'id':2, 'left':3, 'right':4, 'depth':2}, []),
          (u"child212", {'id':2, 'left':5, 'right':12, 'depth':2}, [
            (u"child2121", {'id':2, 'left':6, 'right':7, 'depth':3}, []),
            (u"child2122", {'id':2, 'left':8, 'right':11, 'depth':3}, [
              (u"child21222", {'id':2, 'left':9, 'right':10, 'depth':4}, []),
            ]),
          ]),
        ]),
        (u"child22", {'id':2, 'left':14, 'right':15, 'depth':1}, []),
        (u"child23", {'id':2, 'left':16, 'right':17, 'depth':1}, []),
      ]),
      (u"root3", {'id':3, 'left':1, 'right':2, 'depth':0}, []),
    ]
    self._delete_helper(name, result)
  def test_del_child21222(self):
    name = u"child21222"
    result = [
      (u"root1", {'id':1, 'left':1, 'right':8, 'depth':0}, [
        (u"child11", {'id':1, 'left':2, 'right':3, 'depth':1}, []),
        (u"child12", {'id':1, 'left':4, 'right':5, 'depth':1}, []),
        (u"child13", {'id':1, 'left':6, 'right':7, 'depth':1}, []),
      ]),
      (u"root2", {'id':2, 'left':1, 'right':18, 'depth':0}, [
        (u"child21", {'id':2, 'left':2, 'right':13, 'depth':1}, [
          (u"child211", {'id':2, 'left':3, 'right':4, 'depth':2}, []),
          (u"child212", {'id':2, 'left':5, 'right':12, 'depth':2}, [
            (u"child2121", {'id':2, 'left':6, 'right':7, 'depth':3}, []),
            (u"child2122", {'id':2, 'left':8, 'right':11, 'depth':3}, [
              (u"child21221", {'id':2, 'left':9, 'right':10, 'depth':4}, []),
            ]),
          ]),
        ]),
        (u"child22", {'id':2, 'left':14, 'right':15, 'depth':1}, []),
        (u"child23", {'id':2, 'left':16, 'right':17, 'depth':1}, []),
      ]),
      (u"root3", {'id':3, 'left':1, 'right':2, 'depth':0}, []),
    ]
    self._delete_helper(name, result)
  def test_del_child22(self):
    name = u"child22"
    result = [
      (u"root1", {'id':1, 'left':1, 'right':8, 'depth':0}, [
        (u"child11", {'id':1, 'left':2, 'right':3, 'depth':1}, []),
        (u"child12", {'id':1, 'left':4, 'right':5, 'depth':1}, []),
        (u"child13", {'id':1, 'left':6, 'right':7, 'depth':1}, []),
      ]),
      (u"root2", {'id':2, 'left':1, 'right':18, 'depth':0}, [
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
        (u"child23", {'id':2, 'left':16, 'right':17, 'depth':1}, []),
      ]),
      (u"root3", {'id':3, 'left':1, 'right':2, 'depth':0}, []),
    ]
    self._delete_helper(name, result)
  def test_del_child23(self):
    name = u"child23"
    result = [
      (u"root1", {'id':1, 'left':1, 'right':8, 'depth':0}, [
        (u"child11", {'id':1, 'left':2, 'right':3, 'depth':1}, []),
        (u"child12", {'id':1, 'left':4, 'right':5, 'depth':1}, []),
        (u"child13", {'id':1, 'left':6, 'right':7, 'depth':1}, []),
      ]),
      (u"root2", {'id':2, 'left':1, 'right':18, 'depth':0}, [
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
      ]),
      (u"root3", {'id':3, 'left':1, 'right':2, 'depth':0}, []),
    ]
    self._delete_helper(name, result)
  def test_del_root3(self):
    name = u"root3"
    result = [
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
    ]
    self._delete_helper(name, result)
  combined_del_result = [
    (u"child11", {'id':1, 'left':1, 'right':2, 'depth':0}, []),
    (u"child12", {'id':2, 'left':1, 'right':2, 'depth':0}, []),
    (u"child13", {'id':3, 'left':1, 'right':2, 'depth':0}, []),
    (u"root2", {'id':4, 'left':1, 'right':16, 'depth':0}, [
      (u"child21", {'id':4, 'left':2, 'right':13, 'depth':1}, [
        (u"child211", {'id':4, 'left':3, 'right':4, 'depth':2}, []),
        (u"child2121", {'id':4, 'left':5, 'right':6, 'depth':2}, []),
        (u"child2122", {'id':4, 'left':7, 'right':12, 'depth':2}, [
          (u"child21221", {'id':4, 'left':8, 'right':9, 'depth':3}, []),
          (u"child21222", {'id':4, 'left':10, 'right':11, 'depth':3}, []),
        ]),
      ]),
      (u"child22", {'id':4, 'left':14, 'right':15, 'depth':1}, []),
    ]),
    (u"root3", {'id':5, 'left':1, 'right':2, 'depth':0}, []),
  ]
  def test_combined_del_123(self):
    db.session.delete(db.session.query(Named).filter_by(name='root1').one())
    db.session.delete(db.session.query(Named).filter_by(name='child212').one())
    db.session.delete(db.session.query(Named).filter_by(name='child23').one())
    db.session.commit()
    self.assertEqual(get_tree_details(), self.combined_del_result)
  def test_combined_del_132(self):
    db.session.delete(db.session.query(Named).filter_by(name='root1').one())
    db.session.delete(db.session.query(Named).filter_by(name='child23').one())
    db.session.delete(db.session.query(Named).filter_by(name='child212').one())
    db.session.commit()
    self.assertEqual(get_tree_details(), self.combined_del_result)
  def test_combined_del_213(self):
    db.session.delete(db.session.query(Named).filter_by(name='child212').one())
    db.session.delete(db.session.query(Named).filter_by(name='root1').one())
    db.session.delete(db.session.query(Named).filter_by(name='child23').one())
    db.session.commit()
    self.assertEqual(get_tree_details(), self.combined_del_result)
  def test_combined_del_231(self):
    db.session.delete(db.session.query(Named).filter_by(name='child212').one())
    db.session.delete(db.session.query(Named).filter_by(name='child23').one())
    db.session.delete(db.session.query(Named).filter_by(name='root1').one())
    db.session.commit()
    self.assertEqual(get_tree_details(), self.combined_del_result)
  def test_combined_del_312(self):
    db.session.delete(db.session.query(Named).filter_by(name='child23').one())
    db.session.delete(db.session.query(Named).filter_by(name='root1').one())
    db.session.delete(db.session.query(Named).filter_by(name='child212').one())
    db.session.commit()
    self.assertEqual(get_tree_details(), self.combined_del_result)
  def test_combined_del_321(self):
    db.session.delete(db.session.query(Named).filter_by(name='child23').one())
    db.session.delete(db.session.query(Named).filter_by(name='child212').one())
    db.session.delete(db.session.query(Named).filter_by(name='root1').one())
    db.session.commit()
    self.assertEqual(get_tree_details(), self.combined_del_result)

# ===----------------------------------------------------------------------===

class ExplicitMoveTestCase(NamedTestCase):
  """Test that trees are in the appropriate state after nodes are explicitly
  moved about, and that such reparented items have the correct tree attributes
  defined after a commit."""
  name_pattern = [
    (u"action",               {'id':1, 'left':1,  'right':16, 'depth':0}, [
      (u"platformer",         {'id':1, 'left':2,  'right':9,  'depth':1}, [
        (u"platformer_2d",    {'id':1, 'left':3,  'right':4,  'depth':2}, []),
        (u"platformer_3d",    {'id':1, 'left':5,  'right':6,  'depth':2}, []),
        (u"platformer_4d",    {'id':1, 'left':7,  'right':8,  'depth':2}, []),
      ]),
      (u"shmup",              {'id':1, 'left':10, 'right':15, 'depth':1}, [
        (u"shmup_vertical",   {'id':1, 'left':11, 'right':12, 'depth':2}, []),
        (u"shmup_horizontal", {'id':1, 'left':13, 'right':14, 'depth':2}, []),
      ]),
    ]),
    (u"rpg",                  {'id':2, 'left':1,  'right':6,  'depth':0}, [
      (u"arpg",               {'id':2, 'left':2,  'right':3,  'depth':1}, []),
      (u"trpg",               {'id':2, 'left':4,  'right':5,  'depth':1}, []),
    ]),
  ]
  result_static = [
    ('action', {
      'ancestors': [],
      'parent': [],
      'previous-siblings': [],
      'next-siblings': ['rpg'],
      'children': ['platformer','shmup'],
      'descendants': ['platformer','platformer_2d','platformer_3d',
        'platformer_4d','shmup','shmup_vertical','shmup_horizontal'],
      'leaf-nodes': ['platformer_2d','platformer_3d','platformer_4d',
        'shmup_vertical','shmup_horizontal']}),
    ('platformer', {
      'ancestors': ['action'],
      'parent': ['action'],
      'previous-siblings': [],
      'next-siblings': ['shmup'],
      'children': ['platformer_2d','platformer_3d','platformer_4d'],
      'descendants': ['platformer_2d','platformer_3d','platformer_4d'],
      'leaf-nodes': ['platformer_2d','platformer_3d','platformer_4d']}),
    ('platformer_2d', {
      'ancestors': ['action','platformer'],
      'parent': ['platformer'],
      'previous-siblings': [],
      'next-siblings': ['platformer_3d','platformer_4d'],
      'children': [],
      'descendants': [],
      'leaf-nodes': []}),
    ('platformer_3d', {
      'ancestors': ['action','platformer'],
      'parent': ['platformer'],
      'previous-siblings': ['platformer_2d'],
      'next-siblings': ['platformer_4d'],
      'children': [],
      'descendants': [],
      'leaf-nodes': []}),
    ('platformer_4d', {
      'ancestors': ['action','platformer'],
      'parent': ['platformer'],
      'previous-siblings': ['platformer_2d','platformer_3d'],
      'next-siblings': [],
      'children': [],
      'descendants': [],
      'leaf-nodes': []}),
    ('shmup', {
      'ancestors': ['action'],
      'parent': ['action'],
      'previous-siblings': ['platformer'],
      'next-siblings': [],
      'children': ['shmup_vertical','shmup_horizontal'],
      'descendants': ['shmup_vertical','shmup_horizontal'],
      'leaf-nodes': ['shmup_vertical','shmup_horizontal']}),
    ('shmup_vertical', {
      'ancestors': ['action','shmup'],
      'parent': ['shmup'],
      'previous-siblings': [],
      'next-siblings': ['shmup_horizontal'],
      'children': [],
      'descendants': [],
      'leaf-nodes': []}),
    ('shmup_horizontal', {
      'ancestors': ['action','shmup'],
      'parent': ['shmup'],
      'previous-siblings': ['shmup_vertical'],
      'next-siblings': [],
      'children': [],
      'descendants': [],
      'leaf-nodes': []}),
    ('rpg', {
      'ancestors': [],
      'parent': [],
      'previous-siblings': ['action'],
      'next-siblings': [],
      'children': ['arpg','trpg'],
      'descendants': ['arpg','trpg'],
      'leaf-nodes': ['arpg','trpg']}),
    ('arpg', {
      'ancestors': ['rpg'],
      'parent': ['rpg'],
      'previous-siblings': [],
      'next-siblings': ['trpg'],
      'children': [],
      'descendants': [],
      'leaf-nodes': []}),
    ('trpg', {
      'ancestors': ['rpg'],
      'parent': ['rpg'],
      'previous-siblings': ['arpg'],
      'next-siblings': [],
      'children': [],
      'descendants': [],
      'leaf-nodes': []}),
  ]
  def _do_insert_and_check(self, result, node_name, target_name=None, position=Named.tree.POSITION_LAST_CHILD):
    node   = db.session.query(Named).filter_by(name=node_name).one()
    target = target_name and db.session.query(Named).filter_by(name=target_name).one() or None
    Named.tree.insert(node, target, position)
    db.session.commit()
    self.assertEqual(get_tree_details(), result)
  def test_child_into_root__platformer(self):
    name = u"platformer"
    result = [
      (u"action",               {'id':1, 'left':1,  'right':8,  'depth':0}, [
        (u"shmup",              {'id':1, 'left':2,  'right':7,  'depth':1}, [
          (u"shmup_vertical",   {'id':1, 'left':3,  'right':4,  'depth':2}, []),
          (u"shmup_horizontal", {'id':1, 'left':5,  'right':6,  'depth':2}, []),
        ]),
      ]),
      (u"rpg",                  {'id':2, 'left':1,  'right':6,  'depth':0}, [
        (u"arpg",               {'id':2, 'left':2,  'right':3,  'depth':1}, []),
        (u"trpg",               {'id':2, 'left':4,  'right':5,  'depth':1}, []),
      ]),
      (u"platformer",           {'id':3, 'left':1,  'right':8,  'depth':0}, [
        (u"platformer_2d",      {'id':3, 'left':2,  'right':3,  'depth':1}, []),
        (u"platformer_3d",      {'id':3, 'left':4,  'right':5,  'depth':1}, []),
        (u"platformer_4d",      {'id':3, 'left':6,  'right':7,  'depth':1}, []),
      ]),
    ]
    self._do_insert_and_check(result, name)
  def test_child_into_root__platformer_2d(self):
    name = u"platformer_2d"
    result = [
      (u"action",               {'id':1, 'left':1,  'right':14, 'depth':0}, [
        (u"platformer",         {'id':1, 'left':2,  'right':7,  'depth':1}, [
          (u"platformer_3d",    {'id':1, 'left':3,  'right':4,  'depth':2}, []),
          (u"platformer_4d",    {'id':1, 'left':5,  'right':6,  'depth':2}, []),
        ]),
        (u"shmup",              {'id':1, 'left':8,  'right':13, 'depth':1}, [
          (u"shmup_vertical",   {'id':1, 'left':9,  'right':10, 'depth':2}, []),
          (u"shmup_horizontal", {'id':1, 'left':11, 'right':12, 'depth':2}, []),
        ]),
      ]),
      (u"rpg",                  {'id':2, 'left':1,  'right':6,  'depth':0}, [
        (u"arpg",               {'id':2, 'left':2,  'right':3,  'depth':1}, []),
        (u"trpg",               {'id':2, 'left':4,  'right':5,  'depth':1}, []),
      ]),
      (u"platformer_2d",        {'id':3, 'left':1,  'right':2,  'depth':0}, []),
    ]
    self._do_insert_and_check(result, name)
  def test_child_into_root__platformer_3d(self):
    name = u"platformer_3d"
    result = [
      (u"action",               {'id':1, 'left':1,  'right':14, 'depth':0}, [
        (u"platformer",         {'id':1, 'left':2,  'right':7,  'depth':1}, [
          (u"platformer_2d",    {'id':1, 'left':3,  'right':4,  'depth':2}, []),
          (u"platformer_4d",    {'id':1, 'left':5,  'right':6,  'depth':2}, []),
        ]),
        (u"shmup",              {'id':1, 'left':8,  'right':13, 'depth':1}, [
          (u"shmup_vertical",   {'id':1, 'left':9,  'right':10, 'depth':2}, []),
          (u"shmup_horizontal", {'id':1, 'left':11, 'right':12, 'depth':2}, []),
        ]),
      ]),
      (u"rpg",                  {'id':2, 'left':1,  'right':6,  'depth':0}, [
        (u"arpg",               {'id':2, 'left':2,  'right':3,  'depth':1}, []),
        (u"trpg",               {'id':2, 'left':4,  'right':5,  'depth':1}, []),
      ]),
      (u"platformer_3d",        {'id':3, 'left':1,  'right':2,  'depth':0}, []),
    ]
    self._do_insert_and_check(result, name)
  def test_child_into_root__platformer_4d(self):
    name = u"platformer_4d"
    result = [
      (u"action",               {'id':1, 'left':1,  'right':14, 'depth':0}, [
        (u"platformer",         {'id':1, 'left':2,  'right':7,  'depth':1}, [
          (u"platformer_2d",    {'id':1, 'left':3,  'right':4,  'depth':2}, []),
          (u"platformer_3d",    {'id':1, 'left':5,  'right':6,  'depth':2}, []),
        ]),
        (u"shmup",              {'id':1, 'left':8,  'right':13, 'depth':1}, [
          (u"shmup_vertical",   {'id':1, 'left':9,  'right':10, 'depth':2}, []),
          (u"shmup_horizontal", {'id':1, 'left':11, 'right':12, 'depth':2}, []),
        ]),
      ]),
      (u"rpg",                  {'id':2, 'left':1,  'right':6,  'depth':0}, [
        (u"arpg",               {'id':2, 'left':2,  'right':3,  'depth':1}, []),
        (u"trpg",               {'id':2, 'left':4,  'right':5,  'depth':1}, []),
      ]),
      (u"platformer_4d",        {'id':3, 'left':1,  'right':2,  'depth':0}, []),
    ]
    self._do_insert_and_check(result, name)
  def test_child_into_root__shmup(self):
    name = u"shmup"
    result = [
      (u"action",               {'id':1, 'left':1,  'right':10, 'depth':0}, [
        (u"platformer",         {'id':1, 'left':2,  'right':9,  'depth':1}, [
          (u"platformer_2d",    {'id':1, 'left':3,  'right':4,  'depth':2}, []),
          (u"platformer_3d",    {'id':1, 'left':5,  'right':6,  'depth':2}, []),
          (u"platformer_4d",    {'id':1, 'left':7,  'right':8,  'depth':2}, []),
        ]),
      ]),
      (u"rpg",                  {'id':2, 'left':1,  'right':6,  'depth':0}, [
        (u"arpg",               {'id':2, 'left':2,  'right':3,  'depth':1}, []),
        (u"trpg",               {'id':2, 'left':4,  'right':5,  'depth':1}, []),
      ]),
      (u"shmup",                {'id':3, 'left':1,  'right':6,  'depth':0}, [
        (u"shmup_vertical",     {'id':3, 'left':2,  'right':3,  'depth':1}, []),
        (u"shmup_horizontal",   {'id':3, 'left':4,  'right':5,  'depth':1}, []),
      ]),
    ]
    self._do_insert_and_check(result, name)
  def test_child_into_root__shmup_vertical(self):
    name = u"shmup_vertical"
    result = [
      (u"action",               {'id':1, 'left':1,  'right':14, 'depth':0}, [
        (u"platformer",         {'id':1, 'left':2,  'right':9,  'depth':1}, [
          (u"platformer_2d",    {'id':1, 'left':3,  'right':4,  'depth':2}, []),
          (u"platformer_3d",    {'id':1, 'left':5,  'right':6,  'depth':2}, []),
          (u"platformer_4d",    {'id':1, 'left':7,  'right':8,  'depth':2}, []),
        ]),
        (u"shmup",              {'id':1, 'left':10, 'right':13, 'depth':1}, [
          (u"shmup_horizontal", {'id':1, 'left':11, 'right':12, 'depth':2}, []),
        ]),
      ]),
      (u"rpg",                  {'id':2, 'left':1,  'right':6,  'depth':0}, [
        (u"arpg",               {'id':2, 'left':2,  'right':3,  'depth':1}, []),
        (u"trpg",               {'id':2, 'left':4,  'right':5,  'depth':1}, []),
      ]),
      (u"shmup_vertical",       {'id':3, 'left':1,  'right':2,  'depth':0}, []),
    ]
    self._do_insert_and_check(result, name)
  def test_child_into_root__shmup_horizontal(self):
    name = u"shmup_horizontal"
    result = [
      (u"action",               {'id':1, 'left':1,  'right':14, 'depth':0}, [
        (u"platformer",         {'id':1, 'left':2,  'right':9,  'depth':1}, [
          (u"platformer_2d",    {'id':1, 'left':3,  'right':4,  'depth':2}, []),
          (u"platformer_3d",    {'id':1, 'left':5,  'right':6,  'depth':2}, []),
          (u"platformer_4d",    {'id':1, 'left':7,  'right':8,  'depth':2}, []),
        ]),
        (u"shmup",              {'id':1, 'left':10, 'right':13, 'depth':1}, [
          (u"shmup_vertical",   {'id':1, 'left':11, 'right':12, 'depth':2}, []),
        ]),
      ]),
      (u"rpg",                  {'id':2, 'left':1,  'right':6,  'depth':0}, [
        (u"arpg",               {'id':2, 'left':2,  'right':3,  'depth':1}, []),
        (u"trpg",               {'id':2, 'left':4,  'right':5,  'depth':1}, []),
      ]),
      (u"shmup_horizontal",     {'id':3, 'left':1,  'right':2,  'depth':0}, []),
    ]
    self._do_insert_and_check(result, name)
  def test_child_into_root__arpg(self):
    name = u"arpg"
    result = [
      (u"action",               {'id':1, 'left':1,  'right':16, 'depth':0}, [
        (u"platformer",         {'id':1, 'left':2,  'right':9,  'depth':1}, [
          (u"platformer_2d",    {'id':1, 'left':3,  'right':4,  'depth':2}, []),
          (u"platformer_3d",    {'id':1, 'left':5,  'right':6,  'depth':2}, []),
          (u"platformer_4d",    {'id':1, 'left':7,  'right':8,  'depth':2}, []),
        ]),
        (u"shmup",              {'id':1, 'left':10, 'right':15, 'depth':1}, [
          (u"shmup_vertical",   {'id':1, 'left':11, 'right':12, 'depth':2}, []),
          (u"shmup_horizontal", {'id':1, 'left':13, 'right':14, 'depth':2}, []),
        ]),
      ]),
      (u"rpg",                  {'id':2, 'left':1,  'right':4,  'depth':0}, [
        (u"trpg",               {'id':2, 'left':2,  'right':3,  'depth':1}, []),
      ]),
      (u"arpg",                 {'id':3, 'left':1,  'right':2,  'depth':0}, []),
    ]
    self._do_insert_and_check(result, name)
  def test_child_into_root__trpg(self):
    name = u"trpg"
    result = [
      (u"action",               {'id':1, 'left':1,  'right':16, 'depth':0}, [
        (u"platformer",         {'id':1, 'left':2,  'right':9,  'depth':1}, [
          (u"platformer_2d",    {'id':1, 'left':3,  'right':4,  'depth':2}, []),
          (u"platformer_3d",    {'id':1, 'left':5,  'right':6,  'depth':2}, []),
          (u"platformer_4d",    {'id':1, 'left':7,  'right':8,  'depth':2}, []),
        ]),
        (u"shmup",              {'id':1, 'left':10, 'right':15, 'depth':1}, [
          (u"shmup_vertical",   {'id':1, 'left':11, 'right':12, 'depth':2}, []),
          (u"shmup_horizontal", {'id':1, 'left':13, 'right':14, 'depth':2}, []),
        ]),
      ]),
      (u"rpg",                  {'id':2, 'left':1,  'right':4,  'depth':0}, [
        (u"arpg",               {'id':2, 'left':2,  'right':3,  'depth':1}, []),
      ]),
      (u"trpg",                 {'id':3, 'left':1,  'right':2,  'depth':0}, []),
    ]
    self._do_insert_and_check(result, name)
  def test_make_sibling_of_root__platformer__action__left(self):
    node_name   = u"platformer"
    target_name = u"action"
    position    = Named.tree.POSITION_LEFT
    result = [
      (u"platformer",           {'id':1, 'left':1,  'right':8,  'depth':0}, [
        (u"platformer_2d",      {'id':1, 'left':2,  'right':3,  'depth':1}, []),
        (u"platformer_3d",      {'id':1, 'left':4,  'right':5,  'depth':1}, []),
        (u"platformer_4d",      {'id':1, 'left':6,  'right':7,  'depth':1}, []),
      ]),
      (u"action",               {'id':2, 'left':1,  'right':8,  'depth':0}, [
        (u"shmup",              {'id':2, 'left':2,  'right':7,  'depth':1}, [
          (u"shmup_vertical",   {'id':2, 'left':3,  'right':4,  'depth':2}, []),
          (u"shmup_horizontal", {'id':2, 'left':5,  'right':6,  'depth':2}, []),
        ]),
      ]),
      (u"rpg",                  {'id':3, 'left':1,  'right':6,  'depth':0}, [
        (u"arpg",               {'id':3, 'left':2,  'right':3,  'depth':1}, []),
        (u"trpg",               {'id':3, 'left':4,  'right':5,  'depth':1}, []),
      ]),
    ]
    self._do_insert_and_check(result, node_name, target_name, position)
  def test_make_sibling_of_root__platformer__action__right(self):
    node_name   = u"platformer"
    target_name = u"action"
    position    = Named.tree.POSITION_RIGHT
    result = [
      (u"action",               {'id':1, 'left':1,  'right':8,  'depth':0}, [
        (u"shmup",              {'id':1, 'left':2,  'right':7,  'depth':1}, [
          (u"shmup_vertical",   {'id':1, 'left':3,  'right':4,  'depth':2}, []),
          (u"shmup_horizontal", {'id':1, 'left':5,  'right':6,  'depth':2}, []),
        ]),
      ]),
      (u"platformer",           {'id':2, 'left':1,  'right':8,  'depth':0}, [
        (u"platformer_2d",      {'id':2, 'left':2,  'right':3,  'depth':1}, []),
        (u"platformer_3d",      {'id':2, 'left':4,  'right':5,  'depth':1}, []),
        (u"platformer_4d",      {'id':2, 'left':6,  'right':7,  'depth':1}, []),
      ]),
      (u"rpg",                  {'id':3, 'left':1,  'right':6,  'depth':0}, [
        (u"arpg",               {'id':3, 'left':2,  'right':3,  'depth':1}, []),
        (u"trpg",               {'id':3, 'left':4,  'right':5,  'depth':1}, []),
      ]),
    ]
    self._do_insert_and_check(result, node_name, target_name, position)
  def test_make_sibling_of_root__platformer__rpg__left(self):
    node_name   = u"platformer"
    target_name = u"rpg"
    position    = Named.tree.POSITION_LEFT
    result = [
      (u"action",               {'id':1, 'left':1,  'right':8,  'depth':0}, [
        (u"shmup",              {'id':1, 'left':2,  'right':7,  'depth':1}, [
          (u"shmup_vertical",   {'id':1, 'left':3,  'right':4,  'depth':2}, []),
          (u"shmup_horizontal", {'id':1, 'left':5,  'right':6,  'depth':2}, []),
        ]),
      ]),
      (u"platformer",           {'id':2, 'left':1,  'right':8,  'depth':0}, [
        (u"platformer_2d",      {'id':2, 'left':2,  'right':3,  'depth':1}, []),
        (u"platformer_3d",      {'id':2, 'left':4,  'right':5,  'depth':1}, []),
        (u"platformer_4d",      {'id':2, 'left':6,  'right':7,  'depth':1}, []),
      ]),
      (u"rpg",                  {'id':3, 'left':1,  'right':6,  'depth':0}, [
        (u"arpg",               {'id':3, 'left':2,  'right':3,  'depth':1}, []),
        (u"trpg",               {'id':3, 'left':4,  'right':5,  'depth':1}, []),
      ]),
    ]
    self._do_insert_and_check(result, node_name, target_name, position)
  def test_make_sibling_of_root__platformer__rpg__right(self):
    node_name   = u"platformer"
    target_name = u"rpg"
    position    = Named.tree.POSITION_RIGHT
    result = [
      (u"action",               {'id':1, 'left':1,  'right':8,  'depth':0}, [
        (u"shmup",              {'id':1, 'left':2,  'right':7,  'depth':1}, [
          (u"shmup_vertical",   {'id':1, 'left':3,  'right':4,  'depth':2}, []),
          (u"shmup_horizontal", {'id':1, 'left':5,  'right':6,  'depth':2}, []),
        ]),
      ]),
      (u"rpg",                  {'id':2, 'left':1,  'right':6,  'depth':0}, [
        (u"arpg",               {'id':2, 'left':2,  'right':3,  'depth':1}, []),
        (u"trpg",               {'id':2, 'left':4,  'right':5,  'depth':1}, []),
      ]),
      (u"platformer",           {'id':3, 'left':1,  'right':8,  'depth':0}, [
        (u"platformer_2d",      {'id':3, 'left':2,  'right':3,  'depth':1}, []),
        (u"platformer_3d",      {'id':3, 'left':4,  'right':5,  'depth':1}, []),
        (u"platformer_4d",      {'id':3, 'left':6,  'right':7,  'depth':1}, []),
      ]),
    ]
    self._do_insert_and_check(result, node_name, target_name, position)
  def test_make_sibling_of_root__arpg__action__left(self):
    node_name   = u"arpg"
    target_name = u"action"
    position    = Named.tree.POSITION_LEFT
    result = [
      (u"arpg",                 {'id':1, 'left':1,  'right':2,  'depth':0}, []),
      (u"action",               {'id':2, 'left':1,  'right':16, 'depth':0}, [
        (u"platformer",         {'id':2, 'left':2,  'right':9,  'depth':1}, [
          (u"platformer_2d",    {'id':2, 'left':3,  'right':4,  'depth':2}, []),
          (u"platformer_3d",    {'id':2, 'left':5,  'right':6,  'depth':2}, []),
          (u"platformer_4d",    {'id':2, 'left':7,  'right':8,  'depth':2}, []),
        ]),
        (u"shmup",              {'id':2, 'left':10, 'right':15, 'depth':1}, [
          (u"shmup_vertical",   {'id':2, 'left':11, 'right':12, 'depth':2}, []),
          (u"shmup_horizontal", {'id':2, 'left':13, 'right':14, 'depth':2}, []),
        ]),
      ]),
      (u"rpg",                  {'id':3, 'left':1,  'right':4,  'depth':0}, [
        (u"trpg",               {'id':3, 'left':2,  'right':3,  'depth':1}, []),
      ]),
    ]
    self._do_insert_and_check(result, node_name, target_name, position)
  def test_make_sibling_of_root__arpg__action__right(self):
    node_name   = u"arpg"
    target_name = u"action"
    position    = Named.tree.POSITION_RIGHT
    result = [
      (u"action",               {'id':1, 'left':1,  'right':16, 'depth':0}, [
        (u"platformer",         {'id':1, 'left':2,  'right':9,  'depth':1}, [
          (u"platformer_2d",    {'id':1, 'left':3,  'right':4,  'depth':2}, []),
          (u"platformer_3d",    {'id':1, 'left':5,  'right':6,  'depth':2}, []),
          (u"platformer_4d",    {'id':1, 'left':7,  'right':8,  'depth':2}, []),
        ]),
        (u"shmup",              {'id':1, 'left':10, 'right':15, 'depth':1}, [
          (u"shmup_vertical",   {'id':1, 'left':11, 'right':12, 'depth':2}, []),
          (u"shmup_horizontal", {'id':1, 'left':13, 'right':14, 'depth':2}, []),
        ]),
      ]),
      (u"arpg",                 {'id':2, 'left':1,  'right':2,  'depth':0}, []),
      (u"rpg",                  {'id':3, 'left':1,  'right':4,  'depth':0}, [
        (u"trpg",               {'id':3, 'left':2,  'right':3,  'depth':1}, []),
      ]),
    ]
    self._do_insert_and_check(result, node_name, target_name, position)
  def test_make_sibling_of_root__arpg__action__left(self):
    node_name   = u"arpg"
    target_name = u"rpg"
    position    = Named.tree.POSITION_LEFT
    result = [
      (u"action",               {'id':1, 'left':1,  'right':16, 'depth':0}, [
        (u"platformer",         {'id':1, 'left':2,  'right':9,  'depth':1}, [
          (u"platformer_2d",    {'id':1, 'left':3,  'right':4,  'depth':2}, []),
          (u"platformer_3d",    {'id':1, 'left':5,  'right':6,  'depth':2}, []),
          (u"platformer_4d",    {'id':1, 'left':7,  'right':8,  'depth':2}, []),
        ]),
        (u"shmup",              {'id':1, 'left':10, 'right':15, 'depth':1}, [
          (u"shmup_vertical",   {'id':1, 'left':11, 'right':12, 'depth':2}, []),
          (u"shmup_horizontal", {'id':1, 'left':13, 'right':14, 'depth':2}, []),
        ]),
      ]),
      (u"arpg",                 {'id':2, 'left':1,  'right':2,  'depth':0}, []),
      (u"rpg",                  {'id':3, 'left':1,  'right':4,  'depth':0}, [
        (u"trpg",               {'id':3, 'left':2,  'right':3,  'depth':1}, []),
      ]),
    ]
    self._do_insert_and_check(result, node_name, target_name, position)
  def test_make_sibling_of_root__arpg__action__right(self):
    node_name   = u"arpg"
    target_name = u"rpg"
    position    = Named.tree.POSITION_RIGHT
    result = [
      (u"action",               {'id':1, 'left':1,  'right':16, 'depth':0}, [
        (u"platformer",         {'id':1, 'left':2,  'right':9,  'depth':1}, [
          (u"platformer_2d",    {'id':1, 'left':3,  'right':4,  'depth':2}, []),
          (u"platformer_3d",    {'id':1, 'left':5,  'right':6,  'depth':2}, []),
          (u"platformer_4d",    {'id':1, 'left':7,  'right':8,  'depth':2}, []),
        ]),
        (u"shmup",              {'id':1, 'left':10, 'right':15, 'depth':1}, [
          (u"shmup_vertical",   {'id':1, 'left':11, 'right':12, 'depth':2}, []),
          (u"shmup_horizontal", {'id':1, 'left':13, 'right':14, 'depth':2}, []),
        ]),
      ]),
      (u"rpg",                  {'id':2, 'left':1,  'right':4,  'depth':0}, [
        (u"trpg",               {'id':2, 'left':2,  'right':3,  'depth':1}, []),
      ]),
      (u"arpg",                 {'id':3, 'left':1,  'right':2,  'depth':0}, []),
    ]
    self._do_insert_and_check(result, node_name, target_name, position)
  def test_make_sibling_of_root__action__rpg__left(self):
    node_name   = u"action"
    target_name = u"rpg"
    position    = Named.tree.POSITION_LEFT
    result = [
      (u"action",               {'id':1, 'left':1,  'right':16, 'depth':0}, [
        (u"platformer",         {'id':1, 'left':2,  'right':9,  'depth':1}, [
          (u"platformer_2d",    {'id':1, 'left':3,  'right':4,  'depth':2}, []),
          (u"platformer_3d",    {'id':1, 'left':5,  'right':6,  'depth':2}, []),
          (u"platformer_4d",    {'id':1, 'left':7,  'right':8,  'depth':2}, []),
        ]),
        (u"shmup",              {'id':1, 'left':10, 'right':15, 'depth':1}, [
          (u"shmup_vertical",   {'id':1, 'left':11, 'right':12, 'depth':2}, []),
          (u"shmup_horizontal", {'id':1, 'left':13, 'right':14, 'depth':2}, []),
        ]),
      ]),
      (u"rpg",                  {'id':2, 'left':1,  'right':6,  'depth':0}, [
        (u"arpg",               {'id':2, 'left':2,  'right':3,  'depth':1}, []),
        (u"trpg",               {'id':2, 'left':4,  'right':5,  'depth':1}, []),
      ]),
    ]
    self._do_insert_and_check(result, node_name, target_name, position)
  def test_make_sibling_of_root__action__rpg__right(self):
    node_name   = u"action"
    target_name = u"rpg"
    position    = Named.tree.POSITION_RIGHT
    result = [
      (u"rpg",                  {'id':1, 'left':1,  'right':6,  'depth':0}, [
        (u"arpg",               {'id':1, 'left':2,  'right':3,  'depth':1}, []),
        (u"trpg",               {'id':1, 'left':4,  'right':5,  'depth':1}, []),
      ]),
      (u"action",               {'id':2, 'left':1,  'right':16, 'depth':0}, [
        (u"platformer",         {'id':2, 'left':2,  'right':9,  'depth':1}, [
          (u"platformer_2d",    {'id':2, 'left':3,  'right':4,  'depth':2}, []),
          (u"platformer_3d",    {'id':2, 'left':5,  'right':6,  'depth':2}, []),
          (u"platformer_4d",    {'id':2, 'left':7,  'right':8,  'depth':2}, []),
        ]),
        (u"shmup",              {'id':2, 'left':10, 'right':15, 'depth':1}, [
          (u"shmup_vertical",   {'id':2, 'left':11, 'right':12, 'depth':2}, []),
          (u"shmup_horizontal", {'id':2, 'left':13, 'right':14, 'depth':2}, []),
        ]),
      ]),
    ]
    self._do_insert_and_check(result, node_name, target_name, position)
  def test_make_sibling_of_root__rpg__action__left(self):
    node_name   = u"rpg"
    target_name = u"action"
    position    = Named.tree.POSITION_LEFT
    result = [
      (u"rpg",                  {'id':1, 'left':1,  'right':6,  'depth':0}, [
        (u"arpg",               {'id':1, 'left':2,  'right':3,  'depth':1}, []),
        (u"trpg",               {'id':1, 'left':4,  'right':5,  'depth':1}, []),
      ]),
      (u"action",               {'id':2, 'left':1,  'right':16, 'depth':0}, [
        (u"platformer",         {'id':2, 'left':2,  'right':9,  'depth':1}, [
          (u"platformer_2d",    {'id':2, 'left':3,  'right':4,  'depth':2}, []),
          (u"platformer_3d",    {'id':2, 'left':5,  'right':6,  'depth':2}, []),
          (u"platformer_4d",    {'id':2, 'left':7,  'right':8,  'depth':2}, []),
        ]),
        (u"shmup",              {'id':2, 'left':10, 'right':15, 'depth':1}, [
          (u"shmup_vertical",   {'id':2, 'left':11, 'right':12, 'depth':2}, []),
          (u"shmup_horizontal", {'id':2, 'left':13, 'right':14, 'depth':2}, []),
        ]),
      ]),
    ]
    self._do_insert_and_check(result, node_name, target_name, position)
  def test_make_sibling_of_root__rpg__action__right(self):
    node_name   = u"rpg"
    target_name = u"action"
    position    = Named.tree.POSITION_RIGHT
    result = [
      (u"action",               {'id':1, 'left':1,  'right':16, 'depth':0}, [
        (u"platformer",         {'id':1, 'left':2,  'right':9,  'depth':1}, [
          (u"platformer_2d",    {'id':1, 'left':3,  'right':4,  'depth':2}, []),
          (u"platformer_3d",    {'id':1, 'left':5,  'right':6,  'depth':2}, []),
          (u"platformer_4d",    {'id':1, 'left':7,  'right':8,  'depth':2}, []),
        ]),
        (u"shmup",              {'id':1, 'left':10, 'right':15, 'depth':1}, [
          (u"shmup_vertical",   {'id':1, 'left':11, 'right':12, 'depth':2}, []),
          (u"shmup_horizontal", {'id':1, 'left':13, 'right':14, 'depth':2}, []),
        ]),
      ]),
      (u"rpg",                  {'id':2, 'left':1,  'right':6,  'depth':0}, [
        (u"arpg",               {'id':2, 'left':2,  'right':3,  'depth':1}, []),
        (u"trpg",               {'id':2, 'left':4,  'right':5,  'depth':1}, []),
      ]),
    ]
    self._do_insert_and_check(result, node_name, target_name, position)
  def test_move_root_node__action__rpg__first_child(self):
    node_name   = u"action"
    target_name = u"rpg"
    position    = Named.tree.POSITION_FIRST_CHILD
    result = [
      (u"rpg",                    {'id':1, 'left':1,  'right':22, 'depth':0}, [
        (u"action",               {'id':1, 'left':2,  'right':17, 'depth':1}, [
          (u"platformer",         {'id':1, 'left':3,  'right':10, 'depth':2}, [
            (u"platformer_2d",    {'id':1, 'left':4,  'right':5,  'depth':3}, []),
            (u"platformer_3d",    {'id':1, 'left':6,  'right':7,  'depth':3}, []),
            (u"platformer_4d",    {'id':1, 'left':8,  'right':9,  'depth':3}, []),
          ]),
          (u"shmup",              {'id':1, 'left':11, 'right':16, 'depth':2}, [
            (u"shmup_vertical",   {'id':1, 'left':12, 'right':13, 'depth':3}, []),
            (u"shmup_horizontal", {'id':1, 'left':14, 'right':15, 'depth':3}, []),
          ]),
        ]),
        (u"arpg",                 {'id':1, 'left':18, 'right':19, 'depth':1}, []),
        (u"trpg",                 {'id':1, 'left':20, 'right':21, 'depth':1}, []),
      ]),
    ]
    self._do_insert_and_check(result, node_name, target_name, position)
  def test_move_root_node__action__rpg__last_child(self):
    node_name   = u"action"
    target_name = u"rpg"
    position    = Named.tree.POSITION_LAST_CHILD
    result = [
      (u"rpg",                    {'id':1, 'left':1,  'right':22, 'depth':0}, [
        (u"arpg",                 {'id':1, 'left':2,  'right':3,  'depth':1}, []),
        (u"trpg",                 {'id':1, 'left':4,  'right':5,  'depth':1}, []),
        (u"action",               {'id':1, 'left':6,  'right':21, 'depth':1}, [
          (u"platformer",         {'id':1, 'left':7,  'right':14, 'depth':2}, [
            (u"platformer_2d",    {'id':1, 'left':8,  'right':9,  'depth':3}, []),
            (u"platformer_3d",    {'id':1, 'left':10, 'right':11, 'depth':3}, []),
            (u"platformer_4d",    {'id':1, 'left':12, 'right':13, 'depth':3}, []),
          ]),
          (u"shmup",              {'id':1, 'left':15, 'right':20, 'depth':2}, [
            (u"shmup_vertical",   {'id':1, 'left':16, 'right':17, 'depth':3}, []),
            (u"shmup_horizontal", {'id':1, 'left':18, 'right':19, 'depth':3}, []),
          ]),
        ]),
      ]),
    ]
    self._do_insert_and_check(result, node_name, target_name, position)
  def test_move_root_node__action__arpg__left(self):
    node_name   = u"action"
    target_name = u"arpg"
    position    = Named.tree.POSITION_LEFT
    result = [
      (u"rpg",                    {'id':1, 'left':1,  'right':22, 'depth':0}, [
        (u"action",               {'id':1, 'left':2,  'right':17, 'depth':1}, [
          (u"platformer",         {'id':1, 'left':3,  'right':10, 'depth':2}, [
            (u"platformer_2d",    {'id':1, 'left':4,  'right':5,  'depth':3}, []),
            (u"platformer_3d",    {'id':1, 'left':6,  'right':7,  'depth':3}, []),
            (u"platformer_4d",    {'id':1, 'left':8,  'right':9,  'depth':3}, []),
          ]),
          (u"shmup",              {'id':1, 'left':11, 'right':16, 'depth':2}, [
            (u"shmup_vertical",   {'id':1, 'left':12, 'right':13, 'depth':3}, []),
            (u"shmup_horizontal", {'id':1, 'left':14, 'right':15, 'depth':3}, []),
          ]),
        ]),
        (u"arpg",                 {'id':1, 'left':18, 'right':19, 'depth':1}, []),
        (u"trpg",                 {'id':1, 'left':20, 'right':21, 'depth':1}, []),
      ]),
    ]
    self._do_insert_and_check(result, node_name, target_name, position)
  def test_move_root_node__action__arpg__right(self):
    node_name   = u"action"
    target_name = u"arpg"
    position    = Named.tree.POSITION_RIGHT
    result = [
      (u"rpg",                    {'id':1, 'left':1,  'right':22, 'depth':0}, [
        (u"arpg",                 {'id':1, 'left':2,  'right':3,  'depth':1}, []),
        (u"action",               {'id':1, 'left':4,  'right':19, 'depth':1}, [
          (u"platformer",         {'id':1, 'left':5,  'right':12, 'depth':2}, [
            (u"platformer_2d",    {'id':1, 'left':6,  'right':7,  'depth':3}, []),
            (u"platformer_3d",    {'id':1, 'left':8,  'right':9,  'depth':3}, []),
            (u"platformer_4d",    {'id':1, 'left':10, 'right':11, 'depth':3}, []),
          ]),
          (u"shmup",              {'id':1, 'left':13, 'right':18, 'depth':2}, [
            (u"shmup_vertical",   {'id':1, 'left':14, 'right':15, 'depth':3}, []),
            (u"shmup_horizontal", {'id':1, 'left':16, 'right':17, 'depth':3}, []),
          ]),
        ]),
        (u"trpg",                 {'id':1, 'left':20, 'right':21, 'depth':1}, []),
      ]),
    ]
    self._do_insert_and_check(result, node_name, target_name, position)
  def test_move_root_node__action__arpg__first_child(self):
    node_name   = u"action"
    target_name = u"arpg"
    position    = Named.tree.POSITION_FIRST_CHILD
    result = [
      (u"rpg",                      {'id':1, 'left':1,  'right':22, 'depth':0}, [
        (u"arpg",                   {'id':1, 'left':2,  'right':19, 'depth':1}, [
          (u"action",               {'id':1, 'left':3,  'right':18, 'depth':2}, [
            (u"platformer",         {'id':1, 'left':4,  'right':11, 'depth':3}, [
              (u"platformer_2d",    {'id':1, 'left':5,  'right':6,  'depth':4}, []),
              (u"platformer_3d",    {'id':1, 'left':7,  'right':8,  'depth':4}, []),
              (u"platformer_4d",    {'id':1, 'left':9,  'right':10, 'depth':4}, []),
            ]),
            (u"shmup",              {'id':1, 'left':12, 'right':17, 'depth':3}, [
              (u"shmup_vertical",   {'id':1, 'left':13, 'right':14, 'depth':4}, []),
              (u"shmup_horizontal", {'id':1, 'left':15, 'right':16, 'depth':4}, []),
            ]),
          ]),
        ]),
        (u"trpg",                   {'id':1, 'left':20, 'right':21, 'depth':1}, []),
      ]),
    ]
    self._do_insert_and_check(result, node_name, target_name, position)
  def test_move_root_node__action__arpg__last_child(self):
    node_name   = u"action"
    target_name = u"arpg"
    position    = Named.tree.POSITION_LAST_CHILD
    result = [
      (u"rpg",                      {'id':1, 'left':1,  'right':22, 'depth':0}, [
        (u"arpg",                   {'id':1, 'left':2,  'right':19, 'depth':1}, [
          (u"action",               {'id':1, 'left':3,  'right':18, 'depth':2}, [
            (u"platformer",         {'id':1, 'left':4,  'right':11, 'depth':3}, [
              (u"platformer_2d",    {'id':1, 'left':5,  'right':6,  'depth':4}, []),
              (u"platformer_3d",    {'id':1, 'left':7,  'right':8,  'depth':4}, []),
              (u"platformer_4d",    {'id':1, 'left':9,  'right':10, 'depth':4}, []),
            ]),
            (u"shmup",              {'id':1, 'left':12, 'right':17, 'depth':3}, [
              (u"shmup_vertical",   {'id':1, 'left':13, 'right':14, 'depth':4}, []),
              (u"shmup_horizontal", {'id':1, 'left':15, 'right':16, 'depth':4}, []),
            ]),
          ]),
        ]),
        (u"trpg",                   {'id':1, 'left':20, 'right':21, 'depth':1}, []),
      ]),
    ]
    self._do_insert_and_check(result, node_name, target_name, position)
  def test_move_root_node__action__trpg__left(self):
    node_name   = u"action"
    target_name = u"trpg"
    position    = Named.tree.POSITION_LEFT
    result = [
      (u"rpg",                    {'id':1, 'left':1,  'right':22, 'depth':0}, [
        (u"arpg",                 {'id':1, 'left':2,  'right':3,  'depth':1}, []),
        (u"action",               {'id':1, 'left':4,  'right':19, 'depth':1}, [
          (u"platformer",         {'id':1, 'left':5,  'right':12, 'depth':2}, [
            (u"platformer_2d",    {'id':1, 'left':6,  'right':7,  'depth':3}, []),
            (u"platformer_3d",    {'id':1, 'left':8,  'right':9,  'depth':3}, []),
            (u"platformer_4d",    {'id':1, 'left':10, 'right':11, 'depth':3}, []),
          ]),
          (u"shmup",              {'id':1, 'left':13, 'right':18, 'depth':2}, [
            (u"shmup_vertical",   {'id':1, 'left':14, 'right':15, 'depth':3}, []),
            (u"shmup_horizontal", {'id':1, 'left':16, 'right':17, 'depth':3}, []),
          ]),
        ]),
        (u"trpg",                 {'id':1, 'left':20, 'right':21, 'depth':1}, []),
      ]),
    ]
    self._do_insert_and_check(result, node_name, target_name, position)
  def test_move_root_node__action__trpg__right(self):
    node_name   = u"action"
    target_name = u"trpg"
    position    = Named.tree.POSITION_RIGHT
    result = [
      (u"rpg",                    {'id':1, 'left':1,  'right':22, 'depth':0}, [
        (u"arpg",                 {'id':1, 'left':2,  'right':3,  'depth':1}, []),
        (u"trpg",                 {'id':1, 'left':4,  'right':5,  'depth':1}, []),
        (u"action",               {'id':1, 'left':6,  'right':21, 'depth':1}, [
          (u"platformer",         {'id':1, 'left':7,  'right':14, 'depth':2}, [
            (u"platformer_2d",    {'id':1, 'left':8,  'right':9,  'depth':3}, []),
            (u"platformer_3d",    {'id':1, 'left':10, 'right':11, 'depth':3}, []),
            (u"platformer_4d",    {'id':1, 'left':12, 'right':13, 'depth':3}, []),
          ]),
          (u"shmup",              {'id':1, 'left':15, 'right':20, 'depth':2}, [
            (u"shmup_vertical",   {'id':1, 'left':16, 'right':17, 'depth':3}, []),
            (u"shmup_horizontal", {'id':1, 'left':18, 'right':19, 'depth':3}, []),
          ]),
        ]),
      ]),
    ]
    self._do_insert_and_check(result, node_name, target_name, position)
  def test_move_root_node__action__trpg__first_child(self):
    node_name   = u"action"
    target_name = u"trpg"
    position    = Named.tree.POSITION_FIRST_CHILD
    result = [
      (u"rpg",                      {'id':1, 'left':1,  'right':22, 'depth':0}, [
        (u"arpg",                   {'id':1, 'left':2,  'right':3,  'depth':1}, []),
        (u"trpg",                   {'id':1, 'left':4,  'right':21, 'depth':1}, [
          (u"action",               {'id':1, 'left':5,  'right':20, 'depth':2}, [
            (u"platformer",         {'id':1, 'left':6,  'right':13, 'depth':3}, [
              (u"platformer_2d",    {'id':1, 'left':7,  'right':8,  'depth':4}, []),
              (u"platformer_3d",    {'id':1, 'left':9,  'right':10, 'depth':4}, []),
              (u"platformer_4d",    {'id':1, 'left':11, 'right':12, 'depth':4}, []),
            ]),
            (u"shmup",              {'id':1, 'left':14, 'right':19, 'depth':3}, [
              (u"shmup_vertical",   {'id':1, 'left':15, 'right':16, 'depth':4}, []),
              (u"shmup_horizontal", {'id':1, 'left':17, 'right':18, 'depth':4}, []),
            ]),
          ]),
        ]),
      ]),
    ]
    self._do_insert_and_check(result, node_name, target_name, position)
  def test_move_root_node__action__trpg__last_child(self):
    node_name   = u"action"
    target_name = u"trpg"
    position    = Named.tree.POSITION_LAST_CHILD
    result = [
      (u"rpg",                      {'id':1, 'left':1,  'right':22, 'depth':0}, [
        (u"arpg",                   {'id':1, 'left':2,  'right':3,  'depth':1}, []),
        (u"trpg",                   {'id':1, 'left':4,  'right':21, 'depth':1}, [
          (u"action",               {'id':1, 'left':5,  'right':20, 'depth':2}, [
            (u"platformer",         {'id':1, 'left':6,  'right':13, 'depth':3}, [
              (u"platformer_2d",    {'id':1, 'left':7,  'right':8,  'depth':4}, []),
              (u"platformer_3d",    {'id':1, 'left':9,  'right':10, 'depth':4}, []),
              (u"platformer_4d",    {'id':1, 'left':11, 'right':12, 'depth':4}, []),
            ]),
            (u"shmup",              {'id':1, 'left':14, 'right':19, 'depth':3}, [
              (u"shmup_vertical",   {'id':1, 'left':15, 'right':16, 'depth':4}, []),
              (u"shmup_horizontal", {'id':1, 'left':17, 'right':18, 'depth':4}, []),
            ]),
          ]),
        ]),
      ]),
    ]
    self._do_insert_and_check(result, node_name, target_name, position)
  def test_move_root_node__rpg__action__first_child(self):
    node_name   = u"rpg"
    target_name = u"action"
    position    = Named.tree.POSITION_FIRST_CHILD
    result = [
      (u"action",               {'id':1, 'left':1,  'right':22, 'depth':0}, [
        (u"rpg",                {'id':1, 'left':2,  'right':7,  'depth':1}, [
          (u"arpg",             {'id':1, 'left':3,  'right':4,  'depth':2}, []),
          (u"trpg",             {'id':1, 'left':5,  'right':6,  'depth':2}, []),
        ]),
        (u"platformer",         {'id':1, 'left':8,  'right':15, 'depth':1}, [
          (u"platformer_2d",    {'id':1, 'left':9,  'right':10, 'depth':2}, []),
          (u"platformer_3d",    {'id':1, 'left':11, 'right':12, 'depth':2}, []),
          (u"platformer_4d",    {'id':1, 'left':13, 'right':14, 'depth':2}, []),
        ]),
        (u"shmup",              {'id':1, 'left':16, 'right':21, 'depth':1}, [
          (u"shmup_vertical",   {'id':1, 'left':17, 'right':18, 'depth':2}, []),
          (u"shmup_horizontal", {'id':1, 'left':19, 'right':20, 'depth':2}, []),
        ]),
      ]),
    ]
    self._do_insert_and_check(result, node_name, target_name, position)
  def test_move_root_node__rpg__action__last_child(self):
    node_name   = u"rpg"
    target_name = u"action"
    position    = Named.tree.POSITION_LAST_CHILD
    result = [
      (u"action",               {'id':1, 'left':1,  'right':22, 'depth':0}, [
        (u"platformer",         {'id':1, 'left':2,  'right':9,  'depth':1}, [
          (u"platformer_2d",    {'id':1, 'left':3,  'right':4,  'depth':2}, []),
          (u"platformer_3d",    {'id':1, 'left':5,  'right':6,  'depth':2}, []),
          (u"platformer_4d",    {'id':1, 'left':7,  'right':8,  'depth':2}, []),
        ]),
        (u"shmup",              {'id':1, 'left':10, 'right':15, 'depth':1}, [
          (u"shmup_vertical",   {'id':1, 'left':11, 'right':12, 'depth':2}, []),
          (u"shmup_horizontal", {'id':1, 'left':13, 'right':14, 'depth':2}, []),
        ]),
        (u"rpg",                {'id':1, 'left':16, 'right':21, 'depth':1}, [
          (u"arpg",             {'id':1, 'left':17, 'right':18, 'depth':2}, []),
          (u"trpg",             {'id':1, 'left':19, 'right':20, 'depth':2}, []),
        ]),
      ]),
    ]
    self._do_insert_and_check(result, node_name, target_name, position)
  def test_move_root_node__rpg__platformer__left(self):
    node_name   = u"rpg"
    target_name = u"platformer"
    position    = Named.tree.POSITION_LEFT
    result = [
      (u"action",               {'id':1, 'left':1,  'right':22, 'depth':0}, [
        (u"rpg",                {'id':1, 'left':2,  'right':7,  'depth':1}, [
          (u"arpg",             {'id':1, 'left':3,  'right':4,  'depth':2}, []),
          (u"trpg",             {'id':1, 'left':5,  'right':6,  'depth':2}, []),
        ]),
        (u"platformer",         {'id':1, 'left':8,  'right':15, 'depth':1}, [
          (u"platformer_2d",    {'id':1, 'left':9,  'right':10, 'depth':2}, []),
          (u"platformer_3d",    {'id':1, 'left':11, 'right':12, 'depth':2}, []),
          (u"platformer_4d",    {'id':1, 'left':13, 'right':14, 'depth':2}, []),
        ]),
        (u"shmup",              {'id':1, 'left':16, 'right':21, 'depth':1}, [
          (u"shmup_vertical",   {'id':1, 'left':17, 'right':18, 'depth':2}, []),
          (u"shmup_horizontal", {'id':1, 'left':19, 'right':20, 'depth':2}, []),
        ]),
      ]),
    ]
    self._do_insert_and_check(result, node_name, target_name, position)
  def test_move_root_node__rpg__platformer__right(self):
    node_name   = u"rpg"
    target_name = u"platformer"
    position    = Named.tree.POSITION_RIGHT
    result = [
      (u"action",               {'id':1, 'left':1,  'right':22, 'depth':0}, [
        (u"platformer",         {'id':1, 'left':2,  'right':9,  'depth':1}, [
          (u"platformer_2d",    {'id':1, 'left':3,  'right':4,  'depth':2}, []),
          (u"platformer_3d",    {'id':1, 'left':5,  'right':6,  'depth':2}, []),
          (u"platformer_4d",    {'id':1, 'left':7,  'right':8,  'depth':2}, []),
        ]),
        (u"rpg",                {'id':1, 'left':10, 'right':15, 'depth':1}, [
          (u"arpg",             {'id':1, 'left':11, 'right':12, 'depth':2}, []),
          (u"trpg",             {'id':1, 'left':13, 'right':14, 'depth':2}, []),
        ]),
        (u"shmup",              {'id':1, 'left':16, 'right':21, 'depth':1}, [
          (u"shmup_vertical",   {'id':1, 'left':17, 'right':18, 'depth':2}, []),
          (u"shmup_horizontal", {'id':1, 'left':19, 'right':20, 'depth':2}, []),
        ]),
      ]),
    ]
    self._do_insert_and_check(result, node_name, target_name, position)
  def test_move_root_node__rpg__platformer__first_child(self):
    node_name   = u"rpg"
    target_name = u"platformer"
    position    = Named.tree.POSITION_FIRST_CHILD
    result = [
      (u"action",               {'id':1, 'left':1,  'right':22, 'depth':0}, [
        (u"platformer",         {'id':1, 'left':2,  'right':15, 'depth':1}, [
          (u"rpg",              {'id':1, 'left':3,  'right':8,  'depth':2}, [
            (u"arpg",           {'id':1, 'left':4,  'right':5,  'depth':3}, []),
            (u"trpg",           {'id':1, 'left':6,  'right':7,  'depth':3}, []),
          ]),
          (u"platformer_2d",    {'id':1, 'left':9,  'right':10, 'depth':2}, []),
          (u"platformer_3d",    {'id':1, 'left':11, 'right':12, 'depth':2}, []),
          (u"platformer_4d",    {'id':1, 'left':13, 'right':14, 'depth':2}, []),
        ]),
        (u"shmup",              {'id':1, 'left':16, 'right':21, 'depth':1}, [
          (u"shmup_vertical",   {'id':1, 'left':17, 'right':18, 'depth':2}, []),
          (u"shmup_horizontal", {'id':1, 'left':19, 'right':20, 'depth':2}, []),
        ]),
      ]),
    ]
    self._do_insert_and_check(result, node_name, target_name, position)
  def test_move_root_node__rpg__platformer__last_child(self):
    node_name   = u"rpg"
    target_name = u"platformer"
    position    = Named.tree.POSITION_LAST_CHILD
    result = [
      (u"action",               {'id':1, 'left':1,  'right':22, 'depth':0}, [
        (u"platformer",         {'id':1, 'left':2,  'right':15, 'depth':1}, [
          (u"platformer_2d",    {'id':1, 'left':3,  'right':4,  'depth':2}, []),
          (u"platformer_3d",    {'id':1, 'left':5,  'right':6,  'depth':2}, []),
          (u"platformer_4d",    {'id':1, 'left':7,  'right':8,  'depth':2}, []),
          (u"rpg",              {'id':1, 'left':9,  'right':14, 'depth':2}, [
            (u"arpg",           {'id':1, 'left':10, 'right':11, 'depth':3}, []),
            (u"trpg",           {'id':1, 'left':12, 'right':13, 'depth':3}, []),
          ]),
        ]),
        (u"shmup",              {'id':1, 'left':16, 'right':21, 'depth':1}, [
          (u"shmup_vertical",   {'id':1, 'left':17, 'right':18, 'depth':2}, []),
          (u"shmup_horizontal", {'id':1, 'left':19, 'right':20, 'depth':2}, []),
        ]),
      ]),
    ]
    self._do_insert_and_check(result, node_name, target_name, position)
  def test_move_root_node__rpg__shmup__left(self):
    node_name   = u"rpg"
    target_name = u"shmup"
    position    = Named.tree.POSITION_LEFT
    result = [
      (u"action",               {'id':1, 'left':1,  'right':22, 'depth':0}, [
        (u"platformer",         {'id':1, 'left':2,  'right':9,  'depth':1}, [
          (u"platformer_2d",    {'id':1, 'left':3,  'right':4,  'depth':2}, []),
          (u"platformer_3d",    {'id':1, 'left':5,  'right':6,  'depth':2}, []),
          (u"platformer_4d",    {'id':1, 'left':7,  'right':8,  'depth':2}, []),
        ]),
        (u"rpg",                {'id':1, 'left':10, 'right':15, 'depth':1}, [
          (u"arpg",             {'id':1, 'left':11, 'right':12, 'depth':2}, []),
          (u"trpg",             {'id':1, 'left':13, 'right':14, 'depth':2}, []),
        ]),
        (u"shmup",              {'id':1, 'left':16, 'right':21, 'depth':1}, [
          (u"shmup_vertical",   {'id':1, 'left':17, 'right':18, 'depth':2}, []),
          (u"shmup_horizontal", {'id':1, 'left':19, 'right':20, 'depth':2}, []),
        ]),
      ]),
    ]
    self._do_insert_and_check(result, node_name, target_name, position)
  def test_move_root_node__rpg__shmup__right(self):
    node_name   = u"rpg"
    target_name = u"shmup"
    position    = Named.tree.POSITION_RIGHT
    result = [
      (u"action",               {'id':1, 'left':1,  'right':22, 'depth':0}, [
        (u"platformer",         {'id':1, 'left':2,  'right':9,  'depth':1}, [
          (u"platformer_2d",    {'id':1, 'left':3,  'right':4,  'depth':2}, []),
          (u"platformer_3d",    {'id':1, 'left':5,  'right':6,  'depth':2}, []),
          (u"platformer_4d",    {'id':1, 'left':7,  'right':8,  'depth':2}, []),
        ]),
        (u"shmup",              {'id':1, 'left':10, 'right':15, 'depth':1}, [
          (u"shmup_vertical",   {'id':1, 'left':11, 'right':12, 'depth':2}, []),
          (u"shmup_horizontal", {'id':1, 'left':13, 'right':14, 'depth':2}, []),
        ]),
        (u"rpg",                {'id':1, 'left':16, 'right':21, 'depth':1}, [
          (u"arpg",             {'id':1, 'left':17, 'right':18, 'depth':2}, []),
          (u"trpg",             {'id':1, 'left':19, 'right':20, 'depth':2}, []),
        ]),
      ]),
    ]
    self._do_insert_and_check(result, node_name, target_name, position)
  def test_move_root_node__rpg__shmup__first_child(self):
    node_name   = u"rpg"
    target_name = u"shmup"
    position    = Named.tree.POSITION_FIRST_CHILD
    result = [
      (u"action",               {'id':1, 'left':1,  'right':22, 'depth':0}, [
        (u"platformer",         {'id':1, 'left':2,  'right':9,  'depth':1}, [
          (u"platformer_2d",    {'id':1, 'left':3,  'right':4,  'depth':2}, []),
          (u"platformer_3d",    {'id':1, 'left':5,  'right':6,  'depth':2}, []),
          (u"platformer_4d",    {'id':1, 'left':7,  'right':8,  'depth':2}, []),
        ]),
        (u"shmup",              {'id':1, 'left':10, 'right':21, 'depth':1}, [
          (u"rpg",              {'id':1, 'left':11, 'right':16, 'depth':2}, [
            (u"arpg",           {'id':1, 'left':12, 'right':13, 'depth':3}, []),
            (u"trpg",           {'id':1, 'left':14, 'right':15, 'depth':3}, []),
          ]),
          (u"shmup_vertical",   {'id':1, 'left':17, 'right':18, 'depth':2}, []),
          (u"shmup_horizontal", {'id':1, 'left':19, 'right':20, 'depth':2}, []),
        ]),
      ]),
    ]
    self._do_insert_and_check(result, node_name, target_name, position)
  def test_move_root_node__rpg__shmup__last_child(self):
    node_name   = u"rpg"
    target_name = u"shmup"
    position    = Named.tree.POSITION_LAST_CHILD
    result = [
      (u"action",               {'id':1, 'left':1,  'right':22, 'depth':0}, [
        (u"platformer",         {'id':1, 'left':2,  'right':9,  'depth':1}, [
          (u"platformer_2d",    {'id':1, 'left':3,  'right':4,  'depth':2}, []),
          (u"platformer_3d",    {'id':1, 'left':5,  'right':6,  'depth':2}, []),
          (u"platformer_4d",    {'id':1, 'left':7,  'right':8,  'depth':2}, []),
        ]),
        (u"shmup",              {'id':1, 'left':10, 'right':21, 'depth':1}, [
          (u"shmup_vertical",   {'id':1, 'left':11, 'right':12, 'depth':2}, []),
          (u"shmup_horizontal", {'id':1, 'left':13, 'right':14, 'depth':2}, []),
          (u"rpg",              {'id':1, 'left':15, 'right':20, 'depth':2}, [
            (u"arpg",           {'id':1, 'left':16, 'right':17, 'depth':3}, []),
            (u"trpg",           {'id':1, 'left':18, 'right':19, 'depth':3}, []),
          ]),
        ]),
      ]),
    ]
    self._do_insert_and_check(result, node_name, target_name, position)
  def test_move_root_node__rpg__shmup_vertical__left(self):
    node_name   = u"rpg"
    target_name = u"shmup_vertical"
    position    = Named.tree.POSITION_LEFT
    result = [
      (u"action",               {'id':1, 'left':1,  'right':22, 'depth':0}, [
        (u"platformer",         {'id':1, 'left':2,  'right':9,  'depth':1}, [
          (u"platformer_2d",    {'id':1, 'left':3,  'right':4,  'depth':2}, []),
          (u"platformer_3d",    {'id':1, 'left':5,  'right':6,  'depth':2}, []),
          (u"platformer_4d",    {'id':1, 'left':7,  'right':8,  'depth':2}, []),
        ]),
        (u"shmup",              {'id':1, 'left':10, 'right':21, 'depth':1}, [
          (u"rpg",              {'id':1, 'left':11, 'right':16, 'depth':2}, [
            (u"arpg",           {'id':1, 'left':12, 'right':13, 'depth':3}, []),
            (u"trpg",           {'id':1, 'left':14, 'right':15, 'depth':3}, []),
          ]),
          (u"shmup_vertical",   {'id':1, 'left':17, 'right':18, 'depth':2}, []),
          (u"shmup_horizontal", {'id':1, 'left':19, 'right':20, 'depth':2}, []),
        ]),
      ]),
    ]
    self._do_insert_and_check(result, node_name, target_name, position)
  def test_move_root_node__rpg__shmup_vertical__right(self):
    node_name   = u"rpg"
    target_name = u"shmup_vertical"
    position    = Named.tree.POSITION_RIGHT
    result = [
      (u"action",               {'id':1, 'left':1,  'right':22, 'depth':0}, [
        (u"platformer",         {'id':1, 'left':2,  'right':9,  'depth':1}, [
          (u"platformer_2d",    {'id':1, 'left':3,  'right':4,  'depth':2}, []),
          (u"platformer_3d",    {'id':1, 'left':5,  'right':6,  'depth':2}, []),
          (u"platformer_4d",    {'id':1, 'left':7,  'right':8,  'depth':2}, []),
        ]),
        (u"shmup",              {'id':1, 'left':10, 'right':21, 'depth':1}, [
          (u"shmup_vertical",   {'id':1, 'left':11, 'right':12, 'depth':2}, []),
          (u"rpg",              {'id':1, 'left':13, 'right':18, 'depth':2}, [
            (u"arpg",           {'id':1, 'left':14, 'right':15, 'depth':3}, []),
            (u"trpg",           {'id':1, 'left':16, 'right':17, 'depth':3}, []),
          ]),
          (u"shmup_horizontal", {'id':1, 'left':19, 'right':20, 'depth':2}, []),
        ]),
      ]),
    ]
    self._do_insert_and_check(result, node_name, target_name, position)
  def test_move_root_node__rpg__shmup_vertical__first_child(self):
    node_name   = u"rpg"
    target_name = u"shmup_vertical"
    position    = Named.tree.POSITION_FIRST_CHILD
    result = [
      (u"action",               {'id':1, 'left':1,  'right':22, 'depth':0}, [
        (u"platformer",         {'id':1, 'left':2,  'right':9,  'depth':1}, [
          (u"platformer_2d",    {'id':1, 'left':3,  'right':4,  'depth':2}, []),
          (u"platformer_3d",    {'id':1, 'left':5,  'right':6,  'depth':2}, []),
          (u"platformer_4d",    {'id':1, 'left':7,  'right':8,  'depth':2}, []),
        ]),
        (u"shmup",              {'id':1, 'left':10, 'right':21, 'depth':1}, [
          (u"shmup_vertical",   {'id':1, 'left':11, 'right':18, 'depth':2}, [
            (u"rpg",            {'id':1, 'left':12, 'right':17, 'depth':3}, [
              (u"arpg",         {'id':1, 'left':13, 'right':14, 'depth':4}, []),
              (u"trpg",         {'id':1, 'left':15, 'right':16, 'depth':4}, []),
            ]),
          ]),
          (u"shmup_horizontal", {'id':1, 'left':19, 'right':20, 'depth':2}, []),
        ]),
      ]),
    ]
    self._do_insert_and_check(result, node_name, target_name, position)
  def test_move_root_node__rpg__shmup_vertical__last_child(self):
    node_name   = u"rpg"
    target_name = u"shmup_vertical"
    position    = Named.tree.POSITION_LAST_CHILD
    result = [
      (u"action",               {'id':1, 'left':1,  'right':22, 'depth':0}, [
        (u"platformer",         {'id':1, 'left':2,  'right':9,  'depth':1}, [
          (u"platformer_2d",    {'id':1, 'left':3,  'right':4,  'depth':2}, []),
          (u"platformer_3d",    {'id':1, 'left':5,  'right':6,  'depth':2}, []),
          (u"platformer_4d",    {'id':1, 'left':7,  'right':8,  'depth':2}, []),
        ]),
        (u"shmup",              {'id':1, 'left':10, 'right':21, 'depth':1}, [
          (u"shmup_vertical",   {'id':1, 'left':11, 'right':18, 'depth':2}, [
            (u"rpg",            {'id':1, 'left':12, 'right':17, 'depth':3}, [
              (u"arpg",         {'id':1, 'left':13, 'right':14, 'depth':4}, []),
              (u"trpg",         {'id':1, 'left':15, 'right':16, 'depth':4}, []),
            ]),
          ]),
          (u"shmup_horizontal", {'id':1, 'left':19, 'right':20, 'depth':2}, []),
        ]),
      ]),
    ]
    self._do_insert_and_check(result, node_name, target_name, position)
  def test_move_child_node__platformer__shmup__left(self):
    node_name   = u"platformer"
    target_name = u"shmup"
    position    = Named.tree.POSITION_LEFT
    result = [
      (u"action",               {'id':1, 'left':1,  'right':16, 'depth':0}, [
        (u"platformer",         {'id':1, 'left':2,  'right':9,  'depth':1}, [
          (u"platformer_2d",    {'id':1, 'left':3,  'right':4,  'depth':2}, []),
          (u"platformer_3d",    {'id':1, 'left':5,  'right':6,  'depth':2}, []),
          (u"platformer_4d",    {'id':1, 'left':7,  'right':8,  'depth':2}, []),
        ]),
        (u"shmup",              {'id':1, 'left':10, 'right':15, 'depth':1}, [
          (u"shmup_vertical",   {'id':1, 'left':11, 'right':12, 'depth':2}, []),
          (u"shmup_horizontal", {'id':1, 'left':13, 'right':14, 'depth':2}, []),
        ]),
      ]),
      (u"rpg",                  {'id':2, 'left':1,  'right':6,  'depth':0}, [
        (u"arpg",               {'id':2, 'left':2,  'right':3,  'depth':1}, []),
        (u"trpg",               {'id':2, 'left':4,  'right':5,  'depth':1}, []),
      ]),
    ]
    self._do_insert_and_check(result, node_name, target_name, position)
  def test_move_child_node__platformer__shmup__right(self):
    node_name   = u"platformer"
    target_name = u"shmup"
    position    = Named.tree.POSITION_RIGHT
    result = [
      (u"action",               {'id':1, 'left':1,  'right':16, 'depth':0}, [
        (u"shmup",              {'id':1, 'left':2,  'right':7,  'depth':1}, [
          (u"shmup_vertical",   {'id':1, 'left':3,  'right':4,  'depth':2}, []),
          (u"shmup_horizontal", {'id':1, 'left':5,  'right':6,  'depth':2}, []),
        ]),
        (u"platformer",         {'id':1, 'left':8,  'right':15,  'depth':1}, [
          (u"platformer_2d",    {'id':1, 'left':9,  'right':10,  'depth':2}, []),
          (u"platformer_3d",    {'id':1, 'left':11, 'right':12,  'depth':2}, []),
          (u"platformer_4d",    {'id':1, 'left':13, 'right':14,  'depth':2}, []),
        ]),
      ]),
      (u"rpg",                  {'id':2, 'left':1,  'right':6,  'depth':0}, [
        (u"arpg",               {'id':2, 'left':2,  'right':3,  'depth':1}, []),
        (u"trpg",               {'id':2, 'left':4,  'right':5,  'depth':1}, []),
      ]),
    ]
    self._do_insert_and_check(result, node_name, target_name, position)
  def test_move_child_node__platformer__shmup__first_child(self):
    node_name   = u"platformer"
    target_name = u"shmup"
    position    = Named.tree.POSITION_FIRST_CHILD
    result = [
      (u"action",               {'id':1, 'left':1,  'right':16, 'depth':0}, [
        (u"shmup",              {'id':1, 'left':2,  'right':15, 'depth':1}, [
          (u"platformer",       {'id':1, 'left':3,  'right':10, 'depth':2}, [
            (u"platformer_2d",  {'id':1, 'left':4,  'right':5,  'depth':3}, []),
            (u"platformer_3d",  {'id':1, 'left':6,  'right':7,  'depth':3}, []),
            (u"platformer_4d",  {'id':1, 'left':8,  'right':9,  'depth':3}, []),
          ]),
          (u"shmup_vertical",   {'id':1, 'left':11, 'right':12, 'depth':2}, []),
          (u"shmup_horizontal", {'id':1, 'left':13, 'right':14, 'depth':2}, []),
        ]),
      ]),
      (u"rpg",                  {'id':2, 'left':1,  'right':6,  'depth':0}, [
        (u"arpg",               {'id':2, 'left':2,  'right':3,  'depth':1}, []),
        (u"trpg",               {'id':2, 'left':4,  'right':5,  'depth':1}, []),
      ]),
    ]
    self._do_insert_and_check(result, node_name, target_name, position)
  def test_move_child_node__platformer__shmup__last_child(self):
    node_name   = u"platformer"
    target_name = u"shmup"
    position    = Named.tree.POSITION_LAST_CHILD
    result = [
      (u"action",               {'id':1, 'left':1,  'right':16, 'depth':0}, [
        (u"shmup",              {'id':1, 'left':2,  'right':15, 'depth':1}, [
          (u"shmup_vertical",   {'id':1, 'left':3,  'right':4,  'depth':2}, []),
          (u"shmup_horizontal", {'id':1, 'left':5,  'right':6,  'depth':2}, []),
          (u"platformer",       {'id':1, 'left':7,  'right':14, 'depth':2}, [
            (u"platformer_2d",  {'id':1, 'left':8,  'right':9,  'depth':3}, []),
            (u"platformer_3d",  {'id':1, 'left':10, 'right':11, 'depth':3}, []),
            (u"platformer_4d",  {'id':1, 'left':12, 'right':13, 'depth':3}, []),
          ]),
        ]),
      ]),
      (u"rpg",                  {'id':2, 'left':1,  'right':6,  'depth':0}, [
        (u"arpg",               {'id':2, 'left':2,  'right':3,  'depth':1}, []),
        (u"trpg",               {'id':2, 'left':4,  'right':5,  'depth':1}, []),
      ]),
    ]
    self._do_insert_and_check(result, node_name, target_name, position)
  def test_move_child_node__shmup__platformer__left(self):
    node_name   = u"shmup"
    target_name = u"platformer"
    position    = Named.tree.POSITION_LEFT
    result = [
      (u"action",               {'id':1, 'left':1,  'right':16, 'depth':0}, [
        (u"shmup",              {'id':1, 'left':2,  'right':7,  'depth':1}, [
          (u"shmup_vertical",   {'id':1, 'left':3,  'right':4,  'depth':2}, []),
          (u"shmup_horizontal", {'id':1, 'left':5,  'right':6,  'depth':2}, []),
        ]),
        (u"platformer",         {'id':1, 'left':8,  'right':15,  'depth':1}, [
          (u"platformer_2d",    {'id':1, 'left':9,  'right':10,  'depth':2}, []),
          (u"platformer_3d",    {'id':1, 'left':11, 'right':12,  'depth':2}, []),
          (u"platformer_4d",    {'id':1, 'left':13, 'right':14,  'depth':2}, []),
        ]),
      ]),
      (u"rpg",                  {'id':2, 'left':1,  'right':6,  'depth':0}, [
        (u"arpg",               {'id':2, 'left':2,  'right':3,  'depth':1}, []),
        (u"trpg",               {'id':2, 'left':4,  'right':5,  'depth':1}, []),
      ]),
    ]
    self._do_insert_and_check(result, node_name, target_name, position)
  def test_move_child_node__shmup__platformer__right(self):
    node_name   = u"shmup"
    target_name = u"platformer"
    position    = Named.tree.POSITION_RIGHT
    result = [
      (u"action",               {'id':1, 'left':1,  'right':16, 'depth':0}, [
        (u"platformer",         {'id':1, 'left':2,  'right':9,  'depth':1}, [
          (u"platformer_2d",    {'id':1, 'left':3,  'right':4,  'depth':2}, []),
          (u"platformer_3d",    {'id':1, 'left':5,  'right':6,  'depth':2}, []),
          (u"platformer_4d",    {'id':1, 'left':7,  'right':8,  'depth':2}, []),
        ]),
        (u"shmup",              {'id':1, 'left':10, 'right':15, 'depth':1}, [
          (u"shmup_vertical",   {'id':1, 'left':11, 'right':12, 'depth':2}, []),
          (u"shmup_horizontal", {'id':1, 'left':13, 'right':14, 'depth':2}, []),
        ]),
      ]),
      (u"rpg",                  {'id':2, 'left':1,  'right':6,  'depth':0}, [
        (u"arpg",               {'id':2, 'left':2,  'right':3,  'depth':1}, []),
        (u"trpg",               {'id':2, 'left':4,  'right':5,  'depth':1}, []),
      ]),
    ]
    self._do_insert_and_check(result, node_name, target_name, position)
  def test_move_child_node__shmup__platformer__first_child(self):
    node_name   = u"shmup"
    target_name = u"platformer"
    position    = Named.tree.POSITION_FIRST_CHILD
    result = [
      (u"action",                 {'id':1, 'left':1,  'right':16, 'depth':0}, [
        (u"platformer",           {'id':1, 'left':2,  'right':15, 'depth':1}, [
          (u"shmup",              {'id':1, 'left':3,  'right':8,  'depth':2}, [
            (u"shmup_vertical",   {'id':1, 'left':4,  'right':5,  'depth':3}, []),
            (u"shmup_horizontal", {'id':1, 'left':6,  'right':7,  'depth':3}, []),
          ]),
          (u"platformer_2d",      {'id':1, 'left':9,  'right':10,  'depth':2}, []),
          (u"platformer_3d",      {'id':1, 'left':11, 'right':12,  'depth':2}, []),
          (u"platformer_4d",      {'id':1, 'left':13, 'right':14,  'depth':2}, []),
        ]),
      ]),
      (u"rpg",                    {'id':2, 'left':1,  'right':6,  'depth':0}, [
        (u"arpg",                 {'id':2, 'left':2,  'right':3,  'depth':1}, []),
        (u"trpg",                 {'id':2, 'left':4,  'right':5,  'depth':1}, []),
      ]),
    ]
    self._do_insert_and_check(result, node_name, target_name, position)
  def test_move_child_node__shmup__platformer__last_child(self):
    node_name   = u"shmup"
    target_name = u"platformer"
    position    = Named.tree.POSITION_LAST_CHILD
    result = [
      (u"action",                 {'id':1, 'left':1,  'right':16, 'depth':0}, [
        (u"platformer",           {'id':1, 'left':2,  'right':15, 'depth':1}, [
          (u"platformer_2d",      {'id':1, 'left':3,  'right':4,  'depth':2}, []),
          (u"platformer_3d",      {'id':1, 'left':5,  'right':6,  'depth':2}, []),
          (u"platformer_4d",      {'id':1, 'left':7,  'right':8,  'depth':2}, []),
          (u"shmup",              {'id':1, 'left':9,  'right':14, 'depth':2}, [
            (u"shmup_vertical",   {'id':1, 'left':10, 'right':11, 'depth':3}, []),
            (u"shmup_horizontal", {'id':1, 'left':12, 'right':13, 'depth':3}, []),
          ]),
        ]),
      ]),
      (u"rpg",                    {'id':2, 'left':1,  'right':6,  'depth':0}, [
        (u"arpg",                 {'id':2, 'left':2,  'right':3,  'depth':1}, []),
        (u"trpg",                 {'id':2, 'left':4,  'right':5,  'depth':1}, []),
      ]),
    ]
    self._do_insert_and_check(result, node_name, target_name, position)
  def test_move_child_node__platformer__arpg__left(self):
    node_name   = u"platformer"
    target_name = u"arpg"
    position    = Named.tree.POSITION_LEFT
    result = [
      (u"action",               {'id':1, 'left':1,  'right':8,  'depth':0}, [
        (u"shmup",              {'id':1, 'left':2,  'right':7,  'depth':1}, [
          (u"shmup_vertical",   {'id':1, 'left':3,  'right':4,  'depth':2}, []),
          (u"shmup_horizontal", {'id':1, 'left':5,  'right':6,  'depth':2}, []),
        ]),
      ]),
      (u"rpg",                  {'id':2, 'left':1,  'right':14, 'depth':0}, [
        (u"platformer",         {'id':2, 'left':2,  'right':9,  'depth':1}, [
          (u"platformer_2d",    {'id':2, 'left':3,  'right':4,  'depth':2}, []),
          (u"platformer_3d",    {'id':2, 'left':5,  'right':6,  'depth':2}, []),
          (u"platformer_4d",    {'id':2, 'left':7,  'right':8,  'depth':2}, []),
        ]),
        (u"arpg",               {'id':2, 'left':10, 'right':11, 'depth':1}, []),
        (u"trpg",               {'id':2, 'left':12, 'right':13, 'depth':1}, []),
      ]),
    ]
    self._do_insert_and_check(result, node_name, target_name, position)
  def test_move_child_node__platformer__arpg__right(self):
    node_name   = u"platformer"
    target_name = u"arpg"
    position    = Named.tree.POSITION_RIGHT
    result = [
      (u"action",               {'id':1, 'left':1,  'right':8,  'depth':0}, [
        (u"shmup",              {'id':1, 'left':2,  'right':7,  'depth':1}, [
          (u"shmup_vertical",   {'id':1, 'left':3,  'right':4,  'depth':2}, []),
          (u"shmup_horizontal", {'id':1, 'left':5,  'right':6,  'depth':2}, []),
        ]),
      ]),
      (u"rpg",                  {'id':2, 'left':1,  'right':14, 'depth':0}, [
        (u"arpg",               {'id':2, 'left':2,  'right':3,  'depth':1}, []),
        (u"platformer",         {'id':2, 'left':4,  'right':11, 'depth':1}, [
          (u"platformer_2d",    {'id':2, 'left':5,  'right':6,  'depth':2}, []),
          (u"platformer_3d",    {'id':2, 'left':7,  'right':8,  'depth':2}, []),
          (u"platformer_4d",    {'id':2, 'left':9,  'right':10, 'depth':2}, []),
        ]),
        (u"trpg",               {'id':2, 'left':12, 'right':13, 'depth':1}, []),
      ]),
    ]
    self._do_insert_and_check(result, node_name, target_name, position)
  def test_move_child_node__platformer__arpg__first_child(self):
    node_name   = u"platformer"
    target_name = u"arpg"
    position    = Named.tree.POSITION_FIRST_CHILD
    result = [
      (u"action",               {'id':1, 'left':1,  'right':8,  'depth':0}, [
        (u"shmup",              {'id':1, 'left':2,  'right':7,  'depth':1}, [
          (u"shmup_vertical",   {'id':1, 'left':3,  'right':4,  'depth':2}, []),
          (u"shmup_horizontal", {'id':1, 'left':5,  'right':6,  'depth':2}, []),
        ]),
      ]),
      (u"rpg",                  {'id':2, 'left':1,  'right':14, 'depth':0}, [
        (u"arpg",               {'id':2, 'left':2,  'right':11, 'depth':1}, [
          (u"platformer",       {'id':2, 'left':3,  'right':10, 'depth':2}, [
            (u"platformer_2d",  {'id':2, 'left':4,  'right':5,  'depth':3}, []),
            (u"platformer_3d",  {'id':2, 'left':6,  'right':7,  'depth':3}, []),
            (u"platformer_4d",  {'id':2, 'left':8,  'right':9,  'depth':3}, []),
          ]),
        ]),
        (u"trpg",               {'id':2, 'left':12, 'right':13, 'depth':1}, []),
      ]),
    ]
    self._do_insert_and_check(result, node_name, target_name, position)
  def test_move_child_node__platformer__arpg__last_child(self):
    node_name   = u"platformer"
    target_name = u"arpg"
    position    = Named.tree.POSITION_LAST_CHILD
    result = [
      (u"action",               {'id':1, 'left':1,  'right':8,  'depth':0}, [
        (u"shmup",              {'id':1, 'left':2,  'right':7,  'depth':1}, [
          (u"shmup_vertical",   {'id':1, 'left':3,  'right':4,  'depth':2}, []),
          (u"shmup_horizontal", {'id':1, 'left':5,  'right':6,  'depth':2}, []),
        ]),
      ]),
      (u"rpg",                  {'id':2, 'left':1,  'right':14, 'depth':0}, [
        (u"arpg",               {'id':2, 'left':2,  'right':11, 'depth':1}, [
          (u"platformer",       {'id':2, 'left':3,  'right':10, 'depth':2}, [
            (u"platformer_2d",  {'id':2, 'left':4,  'right':5,  'depth':3}, []),
            (u"platformer_3d",  {'id':2, 'left':6,  'right':7,  'depth':3}, []),
            (u"platformer_4d",  {'id':2, 'left':8,  'right':9,  'depth':3}, []),
          ]),
        ]),
        (u"trpg",               {'id':2, 'left':12, 'right':13, 'depth':1}, []),
      ]),
    ]
    self._do_insert_and_check(result, node_name, target_name, position)
  def test_move_child_node__trpg__shmup__left(self):
    node_name   = u"trpg"
    target_name = u"shmup"
    position    = Named.tree.POSITION_LEFT
    result = [
      (u"action",               {'id':1, 'left':1,  'right':18, 'depth':0}, [
        (u"platformer",         {'id':1, 'left':2,  'right':9,  'depth':1}, [
          (u"platformer_2d",    {'id':1, 'left':3,  'right':4,  'depth':2}, []),
          (u"platformer_3d",    {'id':1, 'left':5,  'right':6,  'depth':2}, []),
          (u"platformer_4d",    {'id':1, 'left':7,  'right':8,  'depth':2}, []),
        ]),
        (u"trpg",               {'id':1, 'left':10, 'right':11, 'depth':1}, []),
        (u"shmup",              {'id':1, 'left':12, 'right':17, 'depth':1}, [
          (u"shmup_vertical",   {'id':1, 'left':13, 'right':14, 'depth':2}, []),
          (u"shmup_horizontal", {'id':1, 'left':15, 'right':16, 'depth':2}, []),
        ]),
      ]),
      (u"rpg",                  {'id':2, 'left':1,  'right':4,  'depth':0}, [
        (u"arpg",               {'id':2, 'left':2,  'right':3,  'depth':1}, []),
      ]),
    ]
    self._do_insert_and_check(result, node_name, target_name, position)
  def test_move_child_node__trpg__shmup__right(self):
    node_name   = u"trpg"
    target_name = u"shmup"
    position    = Named.tree.POSITION_RIGHT
    result = [
      (u"action",               {'id':1, 'left':1,  'right':18, 'depth':0}, [
        (u"platformer",         {'id':1, 'left':2,  'right':9,  'depth':1}, [
          (u"platformer_2d",    {'id':1, 'left':3,  'right':4,  'depth':2}, []),
          (u"platformer_3d",    {'id':1, 'left':5,  'right':6,  'depth':2}, []),
          (u"platformer_4d",    {'id':1, 'left':7,  'right':8,  'depth':2}, []),
        ]),
        (u"shmup",              {'id':1, 'left':10, 'right':15, 'depth':1}, [
          (u"shmup_vertical",   {'id':1, 'left':11, 'right':12, 'depth':2}, []),
          (u"shmup_horizontal", {'id':1, 'left':13, 'right':14, 'depth':2}, []),
        ]),
        (u"trpg",               {'id':1, 'left':16, 'right':17, 'depth':1}, []),
      ]),
      (u"rpg",                  {'id':2, 'left':1,  'right':4,  'depth':0}, [
        (u"arpg",               {'id':2, 'left':2,  'right':3,  'depth':1}, []),
      ]),
    ]
    self._do_insert_and_check(result, node_name, target_name, position)
  def test_move_child_node__trpg__shmup__first_child(self):
    node_name   = u"trpg"
    target_name = u"shmup"
    position    = Named.tree.POSITION_FIRST_CHILD
    result = [
      (u"action",               {'id':1, 'left':1,  'right':18, 'depth':0}, [
        (u"platformer",         {'id':1, 'left':2,  'right':9,  'depth':1}, [
          (u"platformer_2d",    {'id':1, 'left':3,  'right':4,  'depth':2}, []),
          (u"platformer_3d",    {'id':1, 'left':5,  'right':6,  'depth':2}, []),
          (u"platformer_4d",    {'id':1, 'left':7,  'right':8,  'depth':2}, []),
        ]),
        (u"shmup",              {'id':1, 'left':10, 'right':17, 'depth':1}, [
          (u"trpg",             {'id':1, 'left':11, 'right':12, 'depth':2}, []),
          (u"shmup_vertical",   {'id':1, 'left':13, 'right':14, 'depth':2}, []),
          (u"shmup_horizontal", {'id':1, 'left':15, 'right':16, 'depth':2}, []),
        ]),
      ]),
      (u"rpg",                  {'id':2, 'left':1,  'right':4,  'depth':0}, [
        (u"arpg",               {'id':2, 'left':2,  'right':3,  'depth':1}, []),
      ]),
    ]
    self._do_insert_and_check(result, node_name, target_name, position)
  def test_move_child_node__trpg__shmup__last_child(self):
    node_name   = u"trpg"
    target_name = u"shmup"
    position    = Named.tree.POSITION_LAST_CHILD
    result = [
      (u"action",               {'id':1, 'left':1,  'right':18, 'depth':0}, [
        (u"platformer",         {'id':1, 'left':2,  'right':9,  'depth':1}, [
          (u"platformer_2d",    {'id':1, 'left':3,  'right':4,  'depth':2}, []),
          (u"platformer_3d",    {'id':1, 'left':5,  'right':6,  'depth':2}, []),
          (u"platformer_4d",    {'id':1, 'left':7,  'right':8,  'depth':2}, []),
        ]),
        (u"shmup",              {'id':1, 'left':10, 'right':17, 'depth':1}, [
          (u"shmup_vertical",   {'id':1, 'left':11, 'right':12, 'depth':2}, []),
          (u"shmup_horizontal", {'id':1, 'left':13, 'right':14, 'depth':2}, []),
          (u"trpg",             {'id':1, 'left':15, 'right':16, 'depth':2}, []),
        ]),
      ]),
      (u"rpg",                  {'id':2, 'left':1,  'right':4,  'depth':0}, [
        (u"arpg",               {'id':2, 'left':2,  'right':3,  'depth':1}, []),
      ]),
    ]
    self._do_insert_and_check(result, node_name, target_name, position)

# ===----------------------------------------------------------------------===

class Regression__AddAllDifferentIds(TestCase):
  def setUp(self):
    self.maxDiff = None
    db.metadata.drop_all()
    db.metadata.create_all()
    db.session = db.Session()
  def tearDown(self):
    db.session.close()
  def test_add_all(self):
    names = ['root', 'child1', 'child2', 'root2']
    nodes = [Named(name=x) for x in names]
    db.session.add_all(nodes)
    db.session.flush()
    self.assertEqual(
      [(1, 1, 2), (2, 1, 2), (3, 1, 2), (4, 1, 2)],
      sorted(map(lambda x:(x.tree_id, x.tree_left, x.tree_right), nodes)))

# ===----------------------------------------------------------------------===
# End of File
# ===----------------------------------------------------------------------===
