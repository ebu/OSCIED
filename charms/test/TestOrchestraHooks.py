#!/usr/bin/env python2
# -*- coding: utf-8 -*-

#**************************************************************************************************#
#     OPEN-SOURCE CLOUD INFRASTRUCTURE FOR ENCODING AND DISTRIBUTION : TESTS OF COMMON LIBRARY
#
#  Authors   : David Fischer
#  Contact   : david.fischer.ch@gmail.com / david.fischer@hesge.ch
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
# Retrieved from https://github.com/EBU-TI/OSCIED

import os, shutil
from copy import copy
from mock import Mock, call
from nose.tools import assert_equal
from lib.CharmHooks import DEFAULT_OS_ENV
from lib.OrchestraConfig import OrchestraConfig
from lib.OrchestraHooks import OrchestraHooks
from pyutils.pyutils import mock_cmd

CONFIG = {
    'verbose': True, 'root_secret': 'toto', 'nodes_secret': 'abcd',
    'repositories_user': 'oscied', 'repositories_pass': '',
    'webui_repository': 'https://github.com/EBU-TI/OSCIED/charms/oscied-webui',
    'transform_repository': 'https://github.com/EBU-TI/OSCIED/charms/oscied-transform',
    'publisher_repository': 'https://github.com/EBU-TI/OSCIED/charms/oscied-publisher',
    'mongo_admin_password': 'Mongo_admin_1234', 'mongo_nodes_password': 'Mongo_user_1234',
    'rabbit_password': 'Alice_in_wonderland', 'storage_address': '', 'storage_nat_address': '',
    'storage_fstype': '', 'storage_mountpoint': '', 'storage_options': ''
}

OS_ENV = copy(DEFAULT_OS_ENV)
OS_ENV['JUJU_UNIT_NAME'] = 'oscied-orchestra/0'
RETURNS = []


class TestOrchestraHooks(object):

    def setUp(self):
        local_config = OrchestraConfig()
        local_config.write('test.pkl')
        self.hooks = OrchestraHooks(None, CONFIG, 'test.pkl', OS_ENV)
        shutil.copy(self.hooks.local_config.hosts_file, 'hosts')
        shutil.copy('mongodb.conf', 'mongodb_test.conf')
        self.hooks.local_config.hosts_file = 'hosts'  # Avoid writing to system hosts file !
        self.hooks.local_config.mongo_config_file = 'mongodb_test.conf'
        self.hooks.local_config.celery_config_file = 'celeryconfig.py'

    def tearDown(self):
        for f in ('celeryconfig.py', 'hosts', 'mongodb_test.conf', 'test.pkl'):
            os.remove(f)

    def test_config_changed(self):
        self.hooks.cmd = mock_cmd()
        self.hooks.hook_config_changed()
        self.hooks.rabbit_users = Mock(return_value='nodes')
        self.hooks.rabbit_vhosts = Mock(return_value='celery')
        raise self.hooks.cmd.call_args_list

if __name__ == '__main__':
    import nose
    nose.runmodule(argv=[__file__], exit=False)
