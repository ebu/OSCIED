#!/usr/bin/env python
# -*- coding: utf-8 -*-

#**********************************************************************************************************************#
#              OPEN-SOURCE CLOUD INFRASTRUCTURE FOR ENCODING AND DISTRIBUTION : COMMON LIBRARY
#
#  Project Manager : Bram Tullemans (tullemans@ebu.ch)
#  Main Developer  : David Fischer (david.fischer.ch@gmail.com)
#  Copyright       : Copyright (c) 2012-2013 EBU. All rights reserved.
#
#**********************************************************************************************************************#
#
# This file is part of EBU Technology & Innovation OSCIED Project.
#
# This project is free software: you can redistribute it and/or modify it under the terms of the EUPL v. 1.1 as provided
# by the European Commission. This project is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See the European Union Public License for more details.
#
# You should have received a copy of the EUPL General Public License along with this project.
# If not, see he EUPL licence v1.1 is available in 22 languages:
#     22-07-2013, <https://joinup.ec.europa.eu/software/page/eupl/licence-eupl>
#
# Retrieved from https://github.com/ebu/OSCIED

import os
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
      long_description=open(os.path.join(os.path.dirname(__file__), u'README.rst'), u'r', encoding=u'utf-8').read(),
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
