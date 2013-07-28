#!/usr/bin/env python

#**************************************************************************************************#
#              OPEN-SOURCE CLOUD INFRASTRUCTURE FOR ENCODING AND DISTRIBUTION : SCRIPTS
#
#  Authors   : David Fischer
#  Contact   : david.fischer.ch@gmail.com
#  Project   : OSCIED (OS Cloud Infrastructure for Encoding and Distribution)
#  Copyright : 2012-2013 OSCIED Team. All rights reserved.
#**************************************************************************************************#
#
# This file is part of EBU/UER OSCIED Project.
#
# This project is free software: you can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This project is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
# even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this project.
# If not, see <http://www.gnu.org/licenses/>
#
# Retrieved from https://github.com/ebu/OSCIED

from __future__ import print_function

import os, sys
from os.path import dirname, join

# Constants ========================================================================================

# FIXME Current implementation of orchestra doesn't accept external IP you must execute juju-menu.sh
# -> config to update storage's related constants automatically

STORAGE_PRIVATE_IP = ''
STORAGE_MOUNTPOINT = ''
STORAGE_BRICK = ''
RELEASE = 'raring'      # Update this according to your needs
NETWORK_IFACE = 'eth0'  # Update this according to your needs

SCRIPTS_PATH = os.getcwd()
BASE_PATH = dirname(SCRIPTS_PATH)
CHARMS_PATH = join(BASE_PATH, 'charms')
CHARMS_DEPLOY_PATH = join(CHARMS_PATH, 'deploy', RELEASE)
CONFIG_PATH = join(BASE_PATH, 'config')
DOCS_PATH = join(BASE_PATH, 'docs')
MEDIAS_PATH = join(BASE_PATH, 'medias')
TOOLS_PATH = join(BASE_PATH, 'tools')
REFERENCES_PATH = join(DOCS_PATH, 'references')

# Reports related configuration (e.g. listing of components)
REPORT_TOOLS_PLANTUML_BINARY = join(TOOLS_PATH, 'plantuml.jar')
DAVID_REPORT_RELEASE_PATH = join(DOCS_PATH, 'david', 'master_thesis')
DAVID_REPORT_PATH = join(DOCS_PATH, 'david', 'master_thesis_rst')
DAVID_REPORT_BUILD_PATH = join(DAVID_REPORT_PATH, 'build')
DAVID_REPORT_SOURCE_PATH = join(DAVID_REPORT_PATH, 'source')
DAVID_REPORT_UML_PATH = join(DAVID_REPORT_PATH, 'uml')
DAVID_REPORT_COMMON_FILE = join(DAVID_REPORT_SOURCE_PATH, 'common.rst')
DAVID_REPORT_LINKS_FILE = join(DAVID_REPORT_SOURCE_PATH, 'common.rst.links')
DAVID_REPORT_REFERENCES_FILE = join(DAVID_REPORT_SOURCE_PATH, 'appendices-references.rst')

WIKI_BUILD_PATH = join(DOCS_PATH, 'wiki', 'build')
WIKI_SOURCE_PATH = join(DOCS_PATH, 'wiki', 'source')

# # Generated configuration
CONFIG_GEN_PATH = join(CONFIG_PATH, 'generated')
CONFIG_GEN_AUTHS_FILE = join(CONFIG_GEN_PATH, 'auths.list')
CONFIG_GEN_IDS_FILE = join(CONFIG_GEN_PATH, 'ids.list')
CONFIG_GEN_JSON_FILE = join(CONFIG_GEN_PATH, 'json.list')
CONFIG_GEN_UNITS_FILE = join(CONFIG_GEN_PATH, 'units.list')
CONFIG_GEN_CONFIG_FILE = join(CONFIG_GEN_PATH, 'config.yaml')

# # Orchestra related configuration (e.g. initial setup)
CONFIG_API_PATH = join(CONFIG_PATH, 'api')
CONFIG_API_USERS_FILE = join(CONFIG_API_PATH, 'users.csv')
CONFIG_API_MEDIAS_FILE = join(CONFIG_API_PATH, 'medias.csv')
CONFIG_API_TPROFILES_FILE = join(CONFIG_API_PATH, 'tprofiles.csv')

# # JuJu related configuration (e.g. environments)
CONFIG_JUJU_PATH = join(CONFIG_PATH, 'juju')
CONFIG_JUJU_ID_RSA = join(CONFIG_JUJU_PATH, 'id_rsa')
CONFIG_JUJU_ID_RSA_PUB = join(CONFIG_JUJU_PATH, 'id_rsa.pub')
CONFIG_JUJU_ENVS_FILE = join(CONFIG_JUJU_PATH, 'environments.yaml')
CONFIG_JUJU_FILES_PATH = join(CONFIG_PATH, 'juju_files')
CONFIG_JUJU_TEMPL_FILE = join(CONFIG_JUJU_FILES_PATH, 'environments.yaml.template')

CONFIG_SCENARIOS_PATH = join(CONFIG_PATH, 'scenarios')

HOME = os.environ['HOME']
ID_RSA = join(HOME, '.ssh', 'id_rsa')
JUJU_PATH = join(HOME, '.juju')
JUJU_STORAGE_PATH = join(JUJU_PATH, 'storage/')
JUJU_ENVS_FILE = join(JUJU_PATH, 'environments.yaml')

BAD_AUTH = 'charlie@hacker.com:challenge_accepted'


def xprint(message):
    print('[ERROR] %s' % message, file=sys.stderr)
    sys.exit(1)
