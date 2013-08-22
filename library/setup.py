#!/usr/bin/env python
# -*- coding: utf-8 -*-

#**********************************************************************************************************************#
#              OPEN-SOURCE CLOUD INFRASTRUCTURE FOR ENCODING AND DISTRIBUTION : COMMON LIBRARY
#
#  Authors   : David Fischer
#  Contact   : david.fischer.ch@gmail.com
#  Project   : OSCIED (OS Cloud Infrastructure for Encoding and Distribution)
#  Copyright : 2012-2013 OSCIED Team. All rights reserved.
#**********************************************************************************************************************#
#
# This file is part of EBU/UER OSCIED Project.
#
# This project is free software: you can redistribute it and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This project is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this project.
# If not, see <http://www.gnu.org/licenses/>
#
# Retrieved from https://github.com/ebu/OSCIED

from codecs import open
from setuptools import setup, sys

major, minor = sys.version_info[:2]
kwargs = {}
if major >= 3:
    print(u'Converting code to Python 3 helped by 2to3')
    kwargs[u'use_2to3'] = True

# https://pypi.python.org/pypi?%3Aaction=list_classifiers

classifiers = u"""
Development Status :: 4 - Beta
Environment :: Console
Environment :: OpenStack
Environment :: Web Environment
Framework :: Flask
Intended Audience :: Developers
Intended Audience :: Science/Research
Intended Audience :: Information Technology
Intended Audience :: Telecommunications Industry
License :: OSI Approved :: GNU GPLv3
Natural Language :: English
Operating System :: POSIX :: Linux
Programming Language :: Python
Programming Language :: Python :: 2
Programming Language :: Python :: 2.6
Programming Language :: Python :: 2.7
Programming Language :: Python :: Implementation :: CPython
Topic :: Adaptive Technologies
Topic :: Internet :: Proxy Servers
Topic :: Internet :: WWW/HTTP :: HTTP Servers
Topic :: Internet :: WWW/HTTP :: WSGI :: Application
Topic :: Multimedia :: Video
"""

not_yet_tested = u"""
Topic :: Multimedia :: Sound/Audio
Programming Language :: Python :: 3
Programming Language :: Python :: 3.2
Programming Language :: Python :: 3.3
"""

setup(name=u'oscied-lib',
      version=u'2.19.20',
      packages=['oscied_lib'],
      description=u'Library of EBU/UER OSCIED Project',
      long_description=open(u'README.rst', u'r', encoding=u'utf-8').read(),
      author=u'David Fischer',
      author_email=u'david.fischer.ch@gmail.com',
      url=u'https://github.com/ebu/OSCIED',
      license=u'GNU GPLv3',  # FIXME update license
      install_requires=[
            u'configobj',    # FIXME version
            u'celery',       # FIXME version
            u'flask',        # FIXME version
            u'mongomock',    # FIXME version
            u'passlib',      # FIXME version
            u'pyaml',        # FIXME version
            u'pymongo',      # FIXME version
            #'pyutils',     # installed by setup.sh
            u'requests',     # FIXME version
            u'six'],         # FIXME version
      #dependency_links=[u'https://github.com/davidfischer-ch/pyutils/tarball/master#egg=pyutils-2.0.1-beta'],
      setup_requires=[u'coverage', u'mock', u'nose'],
      tests_require=[u'coverage', u'mock', u'nose'],
      # Thanks to https://github.com/graingert/django-browserid/commit/46c763f11f76b2f3ba365b164196794a37494f44
      test_suite="tests.runtests.main",
      **kwargs)
