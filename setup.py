#!/usr/bin/env python
# -*- coding: utf-8 -*-

# === setup.py ------------------------------------------------------------===
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

import os

from distutils.core import setup

VERSION = (0,0,1, 'final', 0)

def get_version():
  version = '%s.%s' % (VERSION[0], VERSION[1])
  if VERSION[2]:
    version = '%s.%s' % (version, VERSION[2])
  if VERSION[3:] == ('alpha', 0):
    version = '%s pre-alpha' % version
  else:
    if VERSION[3] != 'final':
      version = '%s %s' % (version, VERSION[3])
      if VERSION[4] != 0:
        version = '%s%s' % (version, VERSION[4])
  return version

# Compile the list of packages available, because distutils doesn't have an
# easy way to do this.
packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir:
  os.chdir(root_dir)
for dirpath, dirnames, filenames in os.walk('sqlalchemy_tree'):
  # Ignore dirnames that start with '.'
  for i, dirname in enumerate(dirnames):
    if dirname.startswith('.'): del dirnames[i]
  if '__init__.py' in filenames:
    pkg = dirpath.replace(os.path.sep, '.')
    if os.path.altsep:
      pkg = pkg.replace(os.path.altsep, '.')
    packages.append(pkg)
  elif filenames:
    prefix = dirpath[16:] # Strip "sqlalchemy_tree/" or "sqlalchemy_tree\"
    for f in filenames:
      data_files.append(os.path.join(prefix, f))

setup(name='SQLAlchemy-ORM-tree',
  version=get_version().replace(' ', '-'),
  description='An implementation for SQLAlchemy-based applications of the nested-sets/modified-pre-order-tree-traversal technique for storing hierarchical data in a relational database.',
  install_requires=['SQLAlchemy>=0.7'],
  author='RokuSigma Inc. and contributors',
  author_email='sqlalchemy-orm-tree@roku-sigma.com',
  maintainer='Mark Friedenbach',
  maintainer_email='mark@roku-sigma.com',
  url='http://www.github.com/rokusigma/sqlalchemy-orm-tree/',
  download_url='http://github.com/rokusigma/sqlalchemy-orm-tree/tarball/master',
  package_dir={'sqlalchemy_tree': 'sqlalchemy_tree'},
  packages=packages,
  package_data={'sqlalchemy_tree': data_files},
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Database',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Utilities',
  ],
)

# ===----------------------------------------------------------------------===
# End of File
# ===----------------------------------------------------------------------===
