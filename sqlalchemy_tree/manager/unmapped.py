#!/usr/bin/env python
# -*- coding: utf-8 -*-

# === sqlalchemy_tree.manager.unmapped ------------------------------------===
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

import sqlalchemy
from sqlalchemy.orm.mapper import class_mapper

from sqlalchemy_tree.options import TreeOptions
from sqlalchemy_tree.orm     import TreeMapperExtension, TreeSessionExtension
from .instance import TreeInstanceManager
from .class_   import TreeClassManager

__all__ = (
  'TreeManager',
)

# ===----------------------------------------------------------------------===

class TreeManager(object):
  """Extension class to create required fields and access class-level and
  instance-level API based on context.

  Basic usage is simple::

    class Node(object):
      mp = sqlalchemy_tree.TreeManager(node_table)

    # After Node is mapped:
    Node.mp.register()

  Now there is an ability to get an instance manager or class manager via the
  property `'mp'` depending on the way in which it is accessed. `Node.mp` will
  return the mapper extension until the class is mapped (useful for setting up
  parameters to pass to the mapper function itself), the class manager
  :class:`TreeClassManager` after mapping, and `instance_node.mp` will return
  instance_node's :class:`TreeInstanceManager`. See those classes for more
  details about their public API's.

  :param table:
    instance of `sqlalchemy.Table`. A table that will be mapped to the node
    class and will hold tree nodes in its rows. The adjacency-list link/self-
    referential foreign-key will be automatically determined, and the
    additional four columns “tree_id”, “left”, “right” and “depth” will
    automatically be added if necessary. :attr:`table` is the only one
    strictly required argument.

  :param parent_id_field=None:
    a self-referencing foreign key field containing the parent node's primary
    key. If this parameter is omitted, it will be guessed joining a `table`
    with itself and using the right part of join's `ON` clause as parent id
    field.

  :param tree_id_field='tree_id':
    the name of the tree id field, or the field object itself. The field will
    be created if the actual parameter value is a string and there is no such
    column in the table :attr:`table`. If the value provided is or names an
    existing SQLAlchemy column object, that object must pass some sanity
    checks: it must be in :attr:`table`, it should have `nullable=False`, and
    be of type :class:`TreeIdField`.

  :param left_field='tree_left':
    the same as for :attr:`tree_id_field`, except that the type of this column
    should be :class:`TreeLeftField`.

  :param left_field='tree_right':
    the same as for :attr:`tree_id_field`, except that the type of this column
    should be :class:`TreeRightField`.

  :param depth_field='tree_depth':
    the same as for :attr:`tree_id_field`, except that the type of this column
    should be :class:`TreeDepthField`.

  :param instance_manager_attr='_tree_instance_manager':
    name for node instance's attribute to cache node's instance manager.

  .. warning::
    Do not change the values of `TreeManager` constructor's arguments after
    saving a first tree node. Doing so will corrupt the tree.
  """
  def __init__(self, *args, **kwargs):
    self.instance_manager_attr = kwargs.pop('instance_manager_attr', \
                                            '_tree_instance_manager')
    kwargs['instance_manager_attr'] = self.instance_manager_attr
    opts = TreeOptions(*args, **kwargs)
    self.options           = opts
    self.class_manager     = None
    self.mapper_extension  = TreeMapperExtension(options=opts)
    self.session_extension = None
    self.root_node_class   = None

  def __get__(self, obj, objtype):
    """There may be three kinds of return values from this getter.

    The first one is used when the class which this descriptor is attached to
    is not yet mapped to any table. In that case the return value is an
    instance of :class:`MPMapperExtension` which is intended to be used as
    mapper extension.

    The second scenario is access to :class:`TreeManager` via mapped class.
    The corresponding :class:`TreeClassManager` instance is returned.

    .. note::
      If the nodes of your tree use polymorphic inheritance it is important to
      know that class manager is accessible only via the base class of
      inheritance hierarchy.

    And the third way is accessing it from the node instance: a
    :class:`TreeInstanceManager` is returned then."""
    # First handle the case of class/extension access:
    if obj is None:
      try:
        # FIXME: Figure out what this root_node_class business is about.
        root_node_class = self._get_root_node_class(objtype)
      except sqlalchemy.orm.exc.UnmappedClassError:
        # SQLAlchemy will helpfully throw an exception if the class is not
        # mapped. This is one of our normal use case scenarios, resulting in
        # the mapper extension being returned:
        return self.mapper_extension

      # FIXME: Figure out what this root_node_class business is about.
      assert objtype is root_node_class, \
             u"TreeClassManager should be accessed via its base class in " \
             u"the polymorphic inheritance hierarchy: %r" % root_node_class

      return self._get_class_manager(root_node_class)

    # Otherwise if obj is specified, an instance manager is requested:
    else:
      # The instance manager is cached on the object itself using a developer-
      # specified attribute name. First see if the cached manager exists:
      instance_manager = getattr(obj, self.instance_manager_attr, None)

      # If the instance manager wasn't found, we create it and cache it on the
      # object:
      if instance_manager is None:
        root_node_class = self._get_root_node_class(objtype)
        instance_manager = TreeInstanceManager(
          class_manager = self._get_class_manager(root_node_class),
          obj           = obj)
        setattr(obj, self.instance_manager_attr, instance_manager)

      # ...and return the instance manager to the caller:
      return instance_manager

  def _get_class_manager(self, objtype):
    "Return an instance of :class:`TreeClassManager`"
    # We cache the class manager on first access, so that it doesn't have to
    # be regenerated every time. It's created on first call to this method and
    # not in __init__ as the class won't be mapped at that time.
    if self.class_manager is None:
      self.session_extension = TreeSessionExtension(
        options=self.options, node_class=objtype)
      self.class_manager = TreeClassManager(
        node_class        = objtype,
        options           = self.options,
        mapper_extension  = self.mapper_extension,
        session_extension = self.session_extension)
      self.options.class_mapped(
        manager = self.class_manager)
    return self.class_manager

  def _get_root_node_class(self, objtype):
    "Get the root node class in the polymorphic inheritance hierarchy."
    # FIXME: Figure out what this root_node_class business is about.
    if self.root_node_class is None:
      mapper = class_mapper(objtype)
      while mapper.inherits is not None:
        mapper = mapper.inherits
      self.root_node_class = mapper.class_
    return self.root_node_class

# ===----------------------------------------------------------------------===
# End of File
# ===----------------------------------------------------------------------===
