#!/usr/bin/env python2
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

from setuptools import setup

# FIXME 2to3 + classifiers ?
kwargs = {}

setup(name='oscied-lib',
      version='2.14.19',
      packages=['oscied_lib'],
      description='Library of EBU/UER OSCIED Project',
      author='David Fischer',
      author_email='david.fischer.ch@gmail.com',
      url='https://github.com/ebu/OSCIED',
      license='GNU GPLv3',  # FIXME update license
      install_requires=[
            'configobj',    # FIXME version
            'celery',       # FIXME version
            'flask',        # FIXME version
            'mongomock',    # FIXME version
            'passlib',      # FIXME version
            'pyaml',        # FIXME version
            'pymongo',      # FIXME version
            #'pyutils',     # installed by setup.sh
            'requests',     # FIXME version
            'six'],         # FIXME version
      #dependency_links=['https://github.com/davidfischer-ch/pyutils/tarball/master#egg=pyutils-2.0.1-beta'],
      setup_requires=['coverage', 'mock', 'nose'],
      tests_require=['coverage', 'mock', 'nose'],
      test_suite='nose.main', **kwargs)
