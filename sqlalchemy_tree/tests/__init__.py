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

# Python standard library unit tests
from unittest2 import TestCase

# SQLAlchemy object-relational mapper
from sqlalchemy import *
from sqlalchemy.orm import mapper, relationship, backref, sessionmaker

# SQLAlchemy tree extension
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
      'parent': [],
      'ancestors': [],
      'children': ['child11','child12','child13'],
      'descendants': ['child11','child12','child13']}),
    (u"child11", {
      'parent': ['root1'],
      'ancestors': ['root1'],
      'children': [],
      'descendants': []}),
    (u"child12", {
      'parent': ['root1'],
      'ancestors': ['root1'],
      'children': [],
      'descendants': []}),
    (u"child13", {
      'parent': ['root1'],
      'ancestors': ['root1'],
      'children': [],
      'descendants': []}),
    (u"root2", {
      'parent': [],
      'ancestors': [],
      'children': ['child21','child22','child23'],
      'descendants': [
        'child21','child211','child212','child2121','child2122','child21221',
        'child21222','child22','child23']}),
    (u"child21", {
      'parent': ['root2'],
      'ancestors': ['root2'],
      'children': ['child211','child212'],
      'descendants': [
        'child211','child212','child2121','child2122','child21221',
        'child21222']}),
    (u"child211", {
      'parent': ['child21'],
      'ancestors': ['root2','child21'],
      'children': [],
      'descendants': []}),
    (u"child212", {
      'parent': ['child21'],
      'ancestors': ['root2','child21'],
      'children': ['child2121','child2122'],
      'descendants': ['child2121','child2122','child21221','child21222']}),
    (u"child2121", {
      'parent': ['child212'],
      'ancestors': ['root2','child21','child212'],
      'children': [],
      'descendants': []}),
    (u"child2122", {
      'parent': ['child212'],
      'ancestors': ['root2','child21','child212'],
      'children': ['child21221','child21222'],
      'descendants': ['child21221','child21222']}),
    (u"child21221", {
      'parent': ['child2122'],
      'ancestors': ['root2','child21','child212','child2122'],
      'children': [],
      'descendants': []}),
    (u"child21222", {
      'parent': ['child2122'],
      'ancestors': ['root2','child21','child212','child2122'],
      'children': [],
      'descendants': []}),
    (u"child22", {
      'parent': ['root2'],
      'ancestors': ['root2'],
      'children': [],
      'descendants': []}),
    (u"child23", {
      'parent': ['root2'],
      'ancestors': ['root2'],
      'children': [],
      'descendants': []}),
    (u"root3", {
      'parent': [],
      'ancestors': [],
      'children': [],
      'descendants': []}),
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
  def test_named_mp_yields_class_manager(self):
    "Named.tree returns an TreeClassManager"
    self.assertTrue(isinstance(Named.tree, TreeClassManager))
  def test_named_mp_yields_instance_manager(self):
    "Named().tree returns an TreeClassManager"
    self.assertTrue(isinstance(Named().tree, TreeInstanceManager))
  def test_filter_root_nodes(self):
    "Verify the root nodes against the expected values"
    expected = sorted([x[0] for x in self.name_pattern])
    self.assertEqual(expected, [x.name for x in
      db.session.query(Named) \
                .filter(Named.tree.filter_root_nodes()) \
                .order_by(Named.name) \
                .all()])
  def test_query_root_nodes(self):
    "Verify the root nodes against the expected values"
    expected = sorted([x[0] for x in self.name_pattern])
    self.assertEqual(expected, [x.name for x in
      Named.tree.query_root_nodes(session=db.session) \
                .order_by(Named.name) \
                .all()])
    node = db.session.query(Named).first()
    self.assertEqual(expected, [x.name for x in
      node.tree.query_root_nodes() \
                .order_by(Named.name) \
                .all()])
  def test_filter_root_node_by_tree_id(self):
    "Verify root node from tree id against expected value"
    def _process_node(root_name, node_name, children):
      node = db.session.query(Named).filter_by(name=node_name).one()
      self.assertEqual(root_name,
        db.session.query(Named) \
                  .filter(Named.tree.filter_root_node_by_tree_id(node.tree_id)) \
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
        Named.tree.query_root_node_by_tree_id(node.tree_id, session=db.session) \
                  .one().name)
      self.assertEqual(root_name,
        node.tree.query_root_node_by_tree_id(node.tree_id) \
                 .one().name)
      for child_name, values, grandchildren in children:
        _process_node(root_name, child_name, grandchildren)
    for root_name, values, children in self.name_pattern:
      _process_node(root_name, root_name, children)
  def test_filter_parent(self):
    "Verify the parent of each node against the expected value"
    for pattern in self.result_static:
      name, result = pattern
      obj = db.session.query(Named).filter_by(name=name).one()
      self.assertEqual(result['parent'],
        map(lambda x:x.name,
          db.session.query(Named).filter(obj.tree.filter_parent()).all()))
  def test_filter_ancestors(self):
    "Verify the ancestors of each node against expected values"
    for pattern in self.result_static:
      name, result = pattern
      obj = db.session.query(Named).filter_by(name=name).one()
      self.assertEqual(result['ancestors'],
        map(lambda x:x.name,
          db.session.query(Named) \
            .filter(obj.tree.filter_ancestors()) \
            .order_by(Named.tree).all()))
      self.assertEqual(result['ancestors'] + [obj.name],
        map(lambda x:x.name,
          db.session.query(Named) \
            .filter(obj.tree.filter_ancestors(and_self=True)) \
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
            obj.tree.query_ancestors(and_self=True).order_by(Named.tree).all()))
  def test_filter_children(self):
    "Verify the children of each node against expected values"
    for pattern in self.result_static:
      name, result = pattern
      obj = db.session.query(Named).filter_by(name=name).one()
      self.assertEqual(result['children'],
        map(lambda x:x.name,
          db.session.query(Named) \
            .filter(obj.tree.filter_children()) \
            .order_by(Named.tree).all()))
  def test_query_children(self):
    "Verify the children of each node against expected values"
    for pattern in self.result_static:
      name, result = pattern
      obj = db.session.query(Named).filter_by(name=name).one()
      self.assertEqual(result['children'],
        map(lambda x:x.name,
            obj.tree.query_children().order_by(Named.tree).all()))
  def test_filter_descendants(self):
    "Verify the descendants of each node against expected values"
    for pattern in self.result_static:
      name, result = pattern
      obj = db.session.query(Named).filter_by(name=name).one()
      self.assertEqual(result['descendants'],
        map(lambda x:x.name,
          db.session.query(Named) \
            .filter(obj.tree.filter_descendants()) \
            .order_by(Named.tree).all()))
      self.assertEqual([obj.name] + result['descendants'],
        map(lambda x:x.name,
          db.session.query(Named) \
            .filter(obj.tree.filter_descendants(and_self=True)) \
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
            obj.tree.query_descendants(and_self=True).order_by(Named.tree).all()))

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
      'parent': [],
      'ancestors': [],
      'children': ['platformer','shmup'],
      'descendants': ['platformer','platformer_2d','platformer_3d','platformer_4d','shmup','shmup_vertical','shmup_horizontal']}),
    ('platformer', {
      'parent': ['action'],
      'ancestors': ['action'],
      'children': ['platformer_2d','platformer_3d','platformer_4d'],
      'descendants': ['platformer_2d','platformer_3d','platformer_4d']}),
    ('platformer_2d', {
      'parent': ['platformer'],
      'ancestors': ['action','platformer'],
      'children': [],
      'descendants': []}),
    ('platformer_3d', {
      'parent': ['platformer'],
      'ancestors': ['action','platformer'],
      'children': [],
      'descendants': []}),
    ('platformer_4d', {
      'parent': ['platformer'],
      'ancestors': ['action','platformer'],
      'children': [],
      'descendants': []}),
    ('shmup', {
      'parent': ['action'],
      'ancestors': ['action'],
      'children': ['shmup_vertical','shmup_horizontal'],
      'descendants': ['shmup_vertical','shmup_horizontal']}),
    ('shmup_vertical', {
      'parent': ['shmup'],
      'ancestors': ['action','shmup'],
      'children': [],
      'descendants': []}),
    ('shmup_horizontal', {
      'parent': ['shmup'],
      'ancestors': ['action','shmup'],
      'children': [],
      'descendants': []}),
    ('rpg', {
      'parent': [],
      'ancestors': [],
      'children': ['arpg','trpg'],
      'descendants': ['arpg','trpg']}),
    ('arpg', {
      'parent': ['rpg'],
      'ancestors': ['rpg'],
      'children': [],
      'descendants': []}),
    ('trpg', {
      'parent': ['rpg'],
      'ancestors': ['rpg'],
      'children': [],
      'descendants': []}),
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
