# -*- coding: utf-8 -*-

#**********************************************************************************************************************#
#              OPEN-SOURCE CLOUD INFRASTRUCTURE FOR ENCODING AND DISTRIBUTION : SCRIPTS
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

from __future__ import print_function

import os, sys
from os.path import dirname, join

# Constants ============================================================================================================

SCRIPTS_PATH = os.getcwd()
BASE_PATH = dirname(SCRIPTS_PATH)
DOCS_PATH = join(BASE_PATH, u'docs')
TOOLS_PATH = join(BASE_PATH, u'tools')

# Reports related configuration (e.g. listing of components)
REPORT_TOOLS_PLANTUML_BINARY = join(TOOLS_PATH, u'plantuml.jar')
DAVID_REPORT_RELEASE_PATH = join(DOCS_PATH, u'david', u'master_thesis')
DAVID_REPORT_PATH = join(DOCS_PATH, u'david', u'master_thesis_rst')
DAVID_REPORT_BUILD_PATH = join(DAVID_REPORT_PATH, u'build')
DAVID_REPORT_SOURCE_PATH = join(DAVID_REPORT_PATH, u'source')
DAVID_REPORT_UML_PATH = join(DAVID_REPORT_PATH, u'uml')
DAVID_REPORT_COMMON_FILE = join(DAVID_REPORT_SOURCE_PATH, u'common.rst')
DAVID_REPORT_LINKS_FILE = join(DAVID_REPORT_SOURCE_PATH, u'common.rst.links')
DAVID_REPORT_REFERENCES_FILE = join(DAVID_REPORT_SOURCE_PATH, u'appendices-references.rst')

WIKI_BUILD_PATH = join(DOCS_PATH, u'wiki', u'build')
WIKI_SOURCE_PATH = join(DOCS_PATH, u'wiki', u'source')


def xprint(message):
    print(u'[ERROR] {0}'.format(message), file=sys.stderr)
    sys.exit(1)
