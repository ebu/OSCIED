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

import os, sys
from os.path import abspath, dirname, join
sys.path.append(abspath(dirname(dirname(__file__))))
sys.path.append(abspath(join(dirname(dirname(__file__)), 'pyutils')))

import shutil
from copy import copy
from mock import call
from nose.tools import assert_equal
from pyutils.pyutils import mock_cmd
from oscied_lib.CharmHooks import DEFAULT_OS_ENV
from oscied_lib.OrchestraConfig import OrchestraConfig
from oscied_lib.OrchestraHooks import OrchestraHooks

CONFIG = {
    'verbose': True, 'root_secret': 'toto', 'nodes_secret': 'abcd',
    'repositories_user': 'oscied', 'repositories_pass': '',
    'charms_repository': 'https://github.com/EBU-TI/OSCIED/charms',
    'mongo_admin_password': 'Mongo_admin_1234', 'mongo_nodes_password': 'Mongo_user_1234',
    'rabbit_password': 'Alice_in_wonderland', 'storage_address': '', 'storage_nat_address': '',
    'storage_fstype': '', 'storage_mountpoint': '', 'storage_options': ''
}

OS_ENV = copy(DEFAULT_OS_ENV)
OS_ENV['JUJU_UNIT_NAME'] = 'oscied-orchestra/0'
RETURNS = []


class OrchestraHooks_tmp(OrchestraHooks):
    def __init__(self, m, c, l, o):
        super(OrchestraHooks_tmp, self).__init__(m, c, l, o)

    @property
    def rabbit_users(self):
        return ['nodes']

    @property
    def rabbit_vhosts(self):
        return ['celery']

class TestOrchestraHooks(object):

    def setUp(self):
        OrchestraConfig().write('test.pkl')
        self.hooks = OrchestraHooks_tmp(None, CONFIG, 'test.pkl', OS_ENV)
        shutil.copy(self.hooks.local_config.hosts_file, 'hosts')
        shutil.copy('mongodb.conf', 'mongodb_test.conf')
        self.hooks.local_config.hosts_file = 'hosts'  # Avoid writing to system hosts file !
        self.hooks.local_config.celery_config_file = 'celeryconfig.py'
        self.hooks.local_config.celery_template_file = os.path.join(
            '../oscied-orchestra', self.hooks.local_config.celery_template_file)
        self.hooks.local_config.ssh_template_path = os.path.join(
            '../oscied-orchestra', self.hooks.local_config.ssh_template_path)
        self.hooks.local_config.mongo_config_file = 'mongodb_test.conf'

    def tearDown(self):
        for f in ('celeryconfig.py', 'hosts', 'mongodb_test.conf', 'test.pkl'):
            try:
                os.remove(f)
            except:
                pass

    def test_config_changed(self):
        self.hooks.cmd = mock_cmd()
        self.hooks.hook_config_changed()
        assert_equal(self.hooks.cmd.call_args_list, [
            call('mongo f.js'),
            call('mongo orchestra f.js'),
            call('mongo celery g.js'),
            call('rabbitmqctl delete_user guest',                    fail=False),
            call('rabbitmqctl delete_vhost /',                       fail=False),
            call('rabbitmqctl add_user nodes "Alice_in_wonderland"', fail=False),
            call('rabbitmqctl add_vhost celery',                     fail=False),
            call('rabbitmqctl set_permissions -p celery nodes ".*" ".*" ".*"', fail=False)])

if __name__ == '__main__':
    import nose
    nose.runmodule(argv=[__file__], exit=False)
