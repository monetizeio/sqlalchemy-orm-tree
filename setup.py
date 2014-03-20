#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import sys
from setuptools import setup, find_packages

sys.path.insert(0, os.getcwd())  # we want to grab this:
from package_metadata import p

with open('requirements.txt') as f:
    install_reqs = [line for line in f.read().split('\n') if line]
    tests_reqs = []

if sys.version_info < (2, 7):
    install_reqs += ['argparse']
    tests_reqs += ['unittest2']

readme = open('README.rst').read()
history = open('CHANGES').read().replace('.. :changelog:', '')


readme = open('README.rst').read()
history = open('CHANGES').read().replace('.. :changelog:', '')

setup(
    name=p.title,
    version=p.version,
    description=p.description,
    long_description=readme,
    author=p.author,
    author_email=p.email,
    maintainer='Mark Friedenbach',
    maintainer_email='mark@monetize.io',
    url='http://www.github.com/monetizeio/sqlalchemy-orm-tree/',
    download_url='http://pypi.python.org/packages/source/S/SQLAlchemy-ORM-tree/SQLAlchemy-ORM-tree-%s.tar.gz' % p.version,
    package_dir={'sqlalchemy_tree': 'sqlalchemy_tree'},
    packages=find_packages(),
    install_requires=install_reqs,
    tests_require=tests_reqs,
    test_suite='sqlalchemy_tree.tests',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Database',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ],
)
