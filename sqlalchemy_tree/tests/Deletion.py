#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .helper import unittest, db, Named, get_tree_details
from .Named import NamedTestCase


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
    db.session.delete(db.session.query(Named).filter_by(name=u"root1").one())
    db.session.delete(db.session.query(Named).filter_by(name=u"child212").one())
    db.session.delete(db.session.query(Named).filter_by(name=u"child23").one())
    db.session.commit()
    self.assertEqual(get_tree_details(), self.combined_del_result)
  def test_combined_del_132(self):
    db.session.delete(db.session.query(Named).filter_by(name=u"root1").one())
    db.session.delete(db.session.query(Named).filter_by(name=u"child23").one())
    db.session.delete(db.session.query(Named).filter_by(name=u"child212").one())
    db.session.commit()
    self.assertEqual(get_tree_details(), self.combined_del_result)
  def test_combined_del_213(self):
    db.session.delete(db.session.query(Named).filter_by(name=u"child212").one())
    db.session.delete(db.session.query(Named).filter_by(name=u"root1").one())
    db.session.delete(db.session.query(Named).filter_by(name=u"child23").one())
    db.session.commit()
    self.assertEqual(get_tree_details(), self.combined_del_result)
  def test_combined_del_231(self):
    db.session.delete(db.session.query(Named).filter_by(name=u"child212").one())
    db.session.delete(db.session.query(Named).filter_by(name=u"child23").one())
    db.session.delete(db.session.query(Named).filter_by(name=u"root1").one())
    db.session.commit()
    self.assertEqual(get_tree_details(), self.combined_del_result)
  def test_combined_del_312(self):
    db.session.delete(db.session.query(Named).filter_by(name=u"child23").one())
    db.session.delete(db.session.query(Named).filter_by(name=u"root1").one())
    db.session.delete(db.session.query(Named).filter_by(name=u"child212").one())
    db.session.commit()
    self.assertEqual(get_tree_details(), self.combined_del_result)
  def test_combined_del_321(self):
    db.session.delete(db.session.query(Named).filter_by(name=u"child23").one())
    db.session.delete(db.session.query(Named).filter_by(name=u"child212").one())
    db.session.delete(db.session.query(Named).filter_by(name=u"root1").one())
    db.session.commit()
    self.assertEqual(get_tree_details(), self.combined_del_result)

# ===----------------------------------------------------------------------===

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(DeletionTestCase))
    return suite
