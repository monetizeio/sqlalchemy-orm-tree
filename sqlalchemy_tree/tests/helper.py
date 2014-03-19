# -*- coding: utf-8 -*-
# Python standard library, unit testing
try:
    import unittest2 as unittest
except ImportError:  # Python 2.7
    import unittest

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

