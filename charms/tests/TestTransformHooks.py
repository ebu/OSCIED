#!/usr/bin/env python2
# -*- coding: utf-8 -*-

#**************************************************************************************************#
#     OPEN-SOURCE CLOUD INFRASTRUCTURE FOR ENCODING AND DISTRIBUTION : TESTS OF COMMON LIBRARY
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

import os, sys
from os.path import abspath, dirname, join
sys.path.append(abspath(dirname(dirname(__file__))))
sys.path.append(abspath(join(dirname(dirname(__file__)), u'pyutils')))

from copy import copy
from nose.tools import assert_equal
from oscied_lib.CharmHooks import DEFAULT_OS_ENV
from oscied_lib.TransformConfig import TransformConfig
from oscied_lib.TransformHooks import TransformHooks

CONFIG_DEFAULT = {
    u'verbose': False, u'concurrency': 1, u'rabbit_queues': u'transform_private',
    u'mongo_connection': u'', u'rabbit_connection': u'', u'api_nat_socket': u'',
    u'storage_address': u'', u'storage_nat_address': u'', u'storage_fstype': u'',
    u'storage_mountpoint': u'', u'storage_options': u''
}

CONFIG_TRANSFORM = {
    'verbose': True, 'concurrency': 2, 'rabbit_queues': 'transform_other',
    'mongo_connection': 'mongodb://tabby:miaow@home.ch:27017/mydb',
    'rabbit_connection': 'another_rabbit_connection', 'api_nat_socket': 'the_nat_socket',
    'storage_address': '', 'storage_nat_address': '', 'storage_fstype': '',
    'storage_mountpoint': '', 'storage_options': ''
}

OS_ENV = copy(DEFAULT_OS_ENV)
OS_ENV[u'JUJU_UNIT_NAME'] = u'oscied-transform/0'
RETURNS = []


class TestTransformHooks(object):

    def create_hooks(self, default_config):
        TransformConfig().write(u'test.pkl')
        hooks = TransformHooks(None, default_config, u'test.pkl', OS_ENV)
        hooks.local_config.storage_mount_sleep_delay = 0.01
        hooks.local_config.hosts_file = u'hosts'  # Avoid writing to system hosts file !
        hooks.local_config.celery_config_file = u'celeryconfig.py'
        hooks.local_config.celery_template_file = os.path.join(
            u'../oscied-transform', hooks.local_config.celery_template_file)
        return hooks

    def tearDown(self):
        for f in (u'celeryconfig.py', u'hosts', u'test.pkl'):
            try:
                os.remove(f)
            except:
                pass

    def test_subordinate_register_default(self):
        self.hooks = self.create_hooks(CONFIG_DEFAULT)
        self.hooks.subordinate_register(
            mongo=u'mongodb://tabby:miaow@home.ch:27017/mydb',
            rabbit=u'the_rabbit_connection')
        assert_equal(self.hooks.local_config.api_nat_socket, u'')
        celeryconfig = {}
        execfile(self.hooks.local_config.celery_config_file, celeryconfig)
        assert_equal(celeryconfig[u'BROKER_URL'], u'the_rabbit_connection')
        assert_equal(celeryconfig[u'CELERY_MONGODB_BACKEND_SETTINGS'], {
            u'host': u'home.ch', u'port': u'27017', u'user': u'tabby', u'password': u'miaow',
            u'database': u'mydb', u'taskmeta_collection': u'taskmeta'})
        assert_equal(celeryconfig[u'CELERYD_CONCURRENCY'], self.hooks.config.concurrency)

    def test_subordinate_register_transform(self):
        self.hooks = self.create_hooks(CONFIG_TRANSFORM)
        self.hooks.local_config.celery_template_file = os.path.join(
            u'../oscied-transform', self.hooks.local_config.celery_template_file)
        self.hooks.subordinate_register(mongo=u'fail', rabbit=u'fail')
        assert_equal(self.hooks.local_config.api_nat_socket, CONFIG_TRANSFORM[u'api_nat_socket'])
        celeryconfig = {}
        execfile(self.hooks.local_config.celery_config_file, celeryconfig)
        assert_equal(celeryconfig[u'BROKER_URL'], CONFIG_TRANSFORM[u'rabbit_connection'])
        assert_equal(celeryconfig[u'CELERY_MONGODB_BACKEND_SETTINGS'], {
            u'host': u'home.ch', u'port': u'27017', u'user': u'tabby', u'password': u'miaow',
            u'database': u'mydb', u'taskmeta_collection': u'taskmeta'})
        assert_equal(celeryconfig[u'CELERYD_CONCURRENCY'], CONFIG_TRANSFORM[u'concurrency'])

if __name__ == u'__main__':
    import nose
    nose.runmodule(argv=[__file__], exit=False)
