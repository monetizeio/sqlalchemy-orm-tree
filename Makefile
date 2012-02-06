# === makefile ------------------------------------------------------------===
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

-include Makefile.local

ROOT=$(shell pwd)
CACHE_ROOT=${ROOT}/.cache
PKG_ROOT=${ROOT}/.pkg

.PHONY: all
all: ${PKG_ROOT}/.stamp-h

.PHONY: check
check: ${PKG_ROOT}/.stamp-h
	mkdir -p build/report/xunit
	echo "\
	import unittest2; \
	import xmlrunner; \
	unittest2.main( \
	  testRunner=xmlrunner.XMLTestRunner(output='build/report/xunit'), \
	  argv=['unit2', 'discover', \
	    '-s','sqlalchemy_tree', \
	    '-p','*.py', \
	    '-t','.', \
	  ] \
	)" >.pytest.py
	chmod +x .pytest.py
	${PKG_ROOT}/bin/coverage run .pytest.py || { rm -f .pytest.py; exit 1; }
	${PKG_ROOT}/bin/coverage xml --omit=".pytest.py" -o build/report/coverage.xml
	rm -f .pytest.py

.PHONY: shell
shell: ${PKG_ROOT}/.stamp-h
	${PKG_ROOT}/bin/ipython

.PHONY: mostlyclean
mostlyclean:

.PHONY: clean
clean: mostlyclean
	-rm -rf dist
	-rm -rf build
	-rm -rf .coverage
	-rm -rf ${PKG_ROOT}

.PHONY: distclean
distclean: clean
	-rm -rf ${CACHE_ROOT}
	-rm -rf Makefile.local

.PHONY: maintainer-clean
maintainer-clean: distclean
	@echo 'This command is intended for maintainers to use; it'
	@echo 'deletes files that may need special tools to rebuild.'

.PHONY: dist
dist:
	${PKG_ROOT}/bin/python setup.py sdist

# ===----------------------------------------------------------------------===

${CACHE_ROOT}/virtualenv/virtualenv-1.7.tar.gz:
	mkdir -p ${CACHE_ROOT}/virtualenv
	sh -c "cd ${CACHE_ROOT}/virtualenv && curl -O http://pypi.python.org/packages/source/v/virtualenv/virtualenv-1.7.tar.gz"

${PKG_ROOT}/.stamp-h: conf/requirements*.pip ${CACHE_ROOT}/virtualenv/virtualenv-1.7.tar.gz
	# Because build and run-time dependencies are not thoroughly tracked,
	# it is entirely possible that rebuilding the development environment
	# on top of an existing one could result in a broken build. For the
	# sake of consistency and preventing unnecessary, difficult-to-debug
	# problems, the entire development environment is rebuilt from scratch
	# everytime this make target is selected.
	${MAKE} clean
	
	# The PKG_ROOT directory, if it exists, is removed by the `clean`
	# target. The PyPI cache is nonexistant if this is a freshly checked-
	# out repository, or if the `distclean` target has been run. Either
	# case might cause problems with build scripts executed later which
	# assume their existence, so they are created now if necessary.
	mkdir -p "${PKG_ROOT}"
	mkdir -p ${CACHE_ROOT}/pypi
	
	# virtualenv is used to create a separate Python installation for this
	# project in PKG_ROOT.
	tar \
	  -C ${CACHE_ROOT}/virtualenv --gzip \
	  -xf ${CACHE_ROOT}/virtualenv/virtualenv-1.7.tar.gz
	python ${CACHE_ROOT}/virtualenv/virtualenv-1.7/virtualenv.py \
	  --clear \
	  --no-site-packages \
	  --distribute \
	  --never-download \
	  --prompt="(SQLAlchemy-ORM-tree) " \
	  ${PKG_ROOT}
	rm -rf ${CACHE_ROOT}/virtualenv/virtualenv-1.7
	
	# readline is installed here to get around a bug on Mac OS X which is
	# causing readline to not build properly if installed from pip.
	${PKG_ROOT}/bin/easy_install readline
	
	# pip is used to install Python dependencies for this project.
	for reqfile in conf/requirements*.pip; do \
	  ${PKG_ROOT}/bin/python ${PKG_ROOT}/bin/pip install \
	    --download-cache=${CACHE_ROOT}/pypi \
	    -r $$reqfile; \
	done
	
	# All done!
	touch ${PKG_ROOT}/.stamp-h

# ===----------------------------------------------------------------------===
# End of File
# ===----------------------------------------------------------------------===
