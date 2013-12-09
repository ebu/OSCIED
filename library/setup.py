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

from __future__ import absolute_import, division, print_function, unicode_literals

import sys
from codecs import open
from pip.req import parse_requirements
from setuptools import setup, find_packages

major, minor = sys.version_info[:2]
kwargs = {}
if major >= 3:
    print('Converting code to Python 3 helped by 2to3')
    kwargs['use_2to3'] = True

# https://pypi.python.org/pypi?%3Aaction=list_classifiers

classifiers = """
Development Status :: 4 - Beta
Environment :: Console
Environment :: OpenStack
Environment :: Web Environment
Framework :: Flask
Intended Audience :: Developers
Intended Audience :: Science/Research
Intended Audience :: Information Technology
Intended Audience :: Telecommunications Industry
License :: OSI Approved :: European Union Public Licence 1.1 (EUPL 1.1)
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

not_yet_tested = """
Topic :: Multimedia :: Sound/Audio
Programming Language :: Python :: 3
Programming Language :: Python :: 3.2
Programming Language :: Python :: 3.3
"""

keywords = [
    'amazon', 'api', 'cloud', 'distribution', 'mpeg-dash', 'juju', 'hybrid cloud', 'maas', 'restful', 'transcoding'
]

install_requires=[
      'configobj',  # FIXME version
      'celery',     # FIXME version
      'flask',      # FIXME version
      'mongomock',  # FIXME version
      'nose',       # FIXME version
      'passlib',    # FIXME version
      #'pytoolbox>=v5.3.13-beta',  # installed by setup.sh
      'pyaml',      # FIXME version
      'pymongo',    # FIXME version
      #'pytoolbox>=v5.3.13-beta',  # installed by setup.sh
      'requests',   # FIXME version
      'six'         # FIXME version
]

setup(name=u'oscied-lib',
      version='2.30.40',
      packages=find_packages(exclude=['tests', 'tests.*']),
      description='Library of EBU/UER OSCIED Project',
      long_description=open('README.rst', 'r', encoding='utf-8').read(),
      author='David Fischer',
      author_email='david.fischer.ch@gmail.com',
      url='https://github.com/ebu/OSCIED',
      license='EUPL 1.1',
      classifiers=filter(None, classifiers.split('\n')),
      keywords=keywords,
      install_requires=[str(requirement.req) for requirement in parse_requirements('REQUIREMENTS.txt')],
      tests_require=['coverage', 'mock', 'nose'],
      # Thanks to https://github.com/graingert/django-browserid/commit/46c763f11f76b2f3ba365b164196794a37494f44
      test_suite='tests.oscied_lib_runtests.main', **kwargs)
