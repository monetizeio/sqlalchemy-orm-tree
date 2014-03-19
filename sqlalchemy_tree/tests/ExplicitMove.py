# -*- coding: utf-8 -*-

from .helper import unittest, Named, db, get_tree_details
from .Named import NamedTestCase


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
    (u"action", {
      'ancestors': [],
      'parent': [],
      'previous-siblings': [],
      'next-siblings': ["rpg"],
      'children': ["platformer","shmup"],
      'descendants': ["platformer","platformer_2d","platformer_3d",
        "platformer_4d","shmup","shmup_vertical","shmup_horizontal"],
      'leaf-nodes': ["platformer_2d","platformer_3d","platformer_4d",
        "shmup_vertical","shmup_horizontal"]}),
    (u"platformer", {
      'ancestors': ["action"],
      'parent': ["action"],
      'previous-siblings': [],
      'next-siblings': ["shmup"],
      'children': ["platformer_2d","platformer_3d","platformer_4d"],
      'descendants': ["platformer_2d","platformer_3d","platformer_4d"],
      'leaf-nodes': ["platformer_2d","platformer_3d","platformer_4d"]}),
    (u"platformer_2d", {
      'ancestors': ["action","platformer"],
      'parent': ["platformer"],
      'previous-siblings': [],
      'next-siblings': ["platformer_3d","platformer_4d"],
      'children': [],
      'descendants': [],
      'leaf-nodes': []}),
    (u"platformer_3d", {
      'ancestors': ["action","platformer"],
      'parent': ["platformer"],
      'previous-siblings': ["platformer_2d"],
      'next-siblings': ["platformer_4d"],
      'children': [],
      'descendants': [],
      'leaf-nodes': []}),
    (u"platformer_4d", {
      'ancestors': ["action","platformer"],
      'parent': ["platformer"],
      'previous-siblings': ["platformer_2d","platformer_3d"],
      'next-siblings': [],
      'children': [],
      'descendants': [],
      'leaf-nodes': []}),
    (u"shmup", {
      'ancestors': ["action"],
      'parent': ["action"],
      'previous-siblings': ["platformer"],
      'next-siblings': [],
      'children': ["shmup_vertical","shmup_horizontal"],
      'descendants': ["shmup_vertical","shmup_horizontal"],
      'leaf-nodes': ["shmup_vertical","shmup_horizontal"]}),
    (u"shmup_vertical", {
      'ancestors': ["action","shmup"],
      'parent': ["shmup"],
      'previous-siblings': [],
      'next-siblings': ["shmup_horizontal"],
      'children': [],
      'descendants': [],
      'leaf-nodes': []}),
    (u"shmup_horizontal", {
      'ancestors': ["action","shmup"],
      'parent': ["shmup"],
      'previous-siblings': ["shmup_vertical"],
      'next-siblings': [],
      'children': [],
      'descendants': [],
      'leaf-nodes': []}),
    (u"rpg", {
      'ancestors': [],
      'parent': [],
      'previous-siblings': ["action"],
      'next-siblings': [],
      'children': ["arpg","trpg"],
      'descendants': ["arpg","trpg"],
      'leaf-nodes': ["arpg","trpg"]}),
    (u"arpg", {
      'ancestors': ["rpg"],
      'parent': ["rpg"],
      'previous-siblings': [],
      'next-siblings': ["trpg"],
      'children': [],
      'descendants': [],
      'leaf-nodes': []}),
    (u"trpg", {
      'ancestors': ["rpg"],
      'parent': ["rpg"],
      'previous-siblings': ["arpg"],
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


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ExplicitMoveTestCase))
    return suite
