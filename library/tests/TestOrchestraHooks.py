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

import os, sys
from os.path import abspath, dirname, expanduser
sys.path.append(abspath(dirname(dirname(__file__))))

import shutil
from copy import copy
from mock import call
from nose.tools import assert_equal
from oscied_lib.pyutils.py_juju import DEFAULT_OS_ENV
from oscied_lib.pyutils.py_unittest import mock_cmd
from oscied_lib.oscied_config import OrchestraLocalConfig
from oscied_lib.OrchestraHooks import OrchestraHooks

CONFIG = {
    u'verbose': True, u'root_secret': u'toto', u'node_secret': u'abcd', u'repositories_user': u'oscied',
    u'repositories_pass': u'', u'charms_repository': u'https://github.com/ebu/OSCIED/charms',
    u'mongo_admin_password': u'Mongo_admin_1234', u'mongo_node_password': u'Mongo_user_1234',
    u'rabbit_password': u'Alice_in_wonderland', u'email_server': u'', u'email_tls': True,
    u'email_address': u'someone@oscied.org', u'email_username': u'someone', u'email_password': u'',
    u'storage_address': u'', u'storage_nat_address': u'', u'storage_fstype': u'', 'storage_mountpoint': u'',
    u'storage_options': u''
}

OS_ENV, RETURNS = copy(DEFAULT_OS_ENV), []
OS_ENV[u'JUJU_UNIT_NAME'] = u'oscied-orchestra/0'


class OrchestraHooks_tmp(OrchestraHooks):
    def __init__(self, m, c, l, o):
        super(OrchestraHooks_tmp, self).__init__(m, c, l, o)

    @property
    def rabbit_users(self):
        return [u'node']

    @property
    def rabbit_vhosts(self):
        return [u'celery']


import oscied_lib.pyutils.py_subprocess
oscied_lib.pyutils.py_subprocess.cmd = mock_cmd()

class TestOrchestraHooks(object):

    def setUp(self):
        OrchestraLocalConfig().write(u'test.pkl')
        self.hooks = OrchestraHooks_tmp(None, CONFIG, u'test.pkl', OS_ENV)
        shutil.copy(self.hooks.local_config.hosts_file, 'hosts')
        shutil.copy(u'mongodb.conf', u'mongodb_test.conf')
        self.hooks.local_config.hosts_file = u'hosts'  # Avoid writing to system hosts file !
        self.hooks.local_config.celery_config_file = u'celeryconfig.py'
        self.hooks.local_config.celery_template_file = os.path.join(
            u'../../charms/oscied-orchestra', self.hooks.local_config.celery_template_file)
        self.hooks.local_config.ssh_template_path = os.path.join(
            u'../../charms/oscied-orchestra', self.hooks.local_config.ssh_template_path)
        self.hooks.local_config.mongo_config_file = u'mongodb_test.conf'

    def tearDown(self):
        for f in (u'celeryconfig.py', u'hosts', u'mongodb_test.conf', u'test.pkl'):
            try:
                os.remove(f)
            except:
                pass

    def test_config_changed(self):
        self.hooks.cmd = mock_cmd()
        self.hooks.hook_config_changed()
        # Check calls of cmd done by rsync
        assert_equal(len(oscied_lib.pyutils.py_subprocess.cmd.call_args_list), 2)
        assert_equal(oscied_lib.pyutils.py_subprocess.cmd.call_args_list[0][0],
                     ([u'rsync', u'-a', u'-r', u'../../charms/oscied-orchestra/ssh/', expanduser(u'~/.ssh/')],))
        assert_equal(oscied_lib.pyutils.py_subprocess.cmd.call_args_list[0][1]['fail'], True)
        assert_equal(oscied_lib.pyutils.py_subprocess.cmd.call_args_list[1][0],
                     ([u'rsync', u'-a', u'-r', u'juju', expanduser(u'~/.juju/')],))
        assert_equal(oscied_lib.pyutils.py_subprocess.cmd.call_args_list[1][1]['fail'], True)
        # Check calls of cmd done by OrchestraHooks
        assert_equal(self.hooks.cmd.call_args_list, [
            call(u'service mongodb start',         fail=False),
            call(u'service rabbitmq-server start', fail=False),
            call(u'mongo f.js'),
            call(u'mongo orchestra f.js'),
            call(u'mongo celery g.js'),
            call(u'rabbitmqctl delete_user guest',                   fail=False),
            call(u'rabbitmqctl delete_vhost /',                      fail=False),
            call(u'rabbitmqctl add_user node "Alice_in_wonderland"', fail=False),
            call(u'rabbitmqctl add_vhost celery',                    fail=False),
            call(u'rabbitmqctl set_permissions -p celery node ".*" ".*" ".*"', fail=False)])

if __name__ == u'__main__':
    import nose
    nose.runmodule(argv=[__file__], exit=False)
