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
sys.path.append(abspath(join(dirname(dirname(__file__)), 'pyutils')))

from copy import copy
from nose.tools import assert_equal
from oscied_lib.CharmHooks import DEFAULT_OS_ENV
from oscied_lib.TransformConfig import TransformConfig
from oscied_lib.TransformHooks import TransformHooks

CONFIG_DEFAULT = {
    'verbose': False, 'concurrency': 1, 'rabbit_queues': 'transform_private',
    'mongo_connection': '', 'rabbit_connection': '', 'api_nat_socket': '', 'storage_address': '',
    'storage_nat_address': '', 'storage_fstype': '', 'storage_mountpoint': '', 'storage_options': ''
}

CONFIG_TRANSFORM = {
    'verbose': True, 'concurrency': 2, 'rabbit_queues': 'transform_other',
    'mongo_connection': 'mongodb://tabby:miaow@home.ch:27017/mydb',
    'rabbit_connection': 'another_rabbit_connection', 'api_nat_socket': 'the_nat_socket',
    'storage_address': '', 'storage_nat_address': '', 'storage_fstype': '',
    'storage_mountpoint': '', 'storage_options': ''
}

OS_ENV = copy(DEFAULT_OS_ENV)
OS_ENV['JUJU_UNIT_NAME'] = 'oscied-transform/0'
RETURNS = []


class TestTransformHooks(object):

    def create_hooks(self, default_config):
        TransformConfig().write('test.pkl')
        hooks = TransformHooks(None, default_config, 'test.pkl', OS_ENV)
        hooks.local_config.storage_mount_sleep_delay = 0.01
        hooks.local_config.hosts_file = 'hosts'  # Avoid writing to system hosts file !
        hooks.local_config.celery_config_file = 'celeryconfig.py'
        hooks.local_config.celery_template_file = os.path.join(
            '../oscied-transform', hooks.local_config.celery_template_file)
        return hooks

    def tearDown(self):
        for f in ('celeryconfig.py', 'hosts', 'test.pkl'):
            try:
                os.remove(f)
            except:
                pass

    def test_subordinate_register_default(self):
        self.hooks = self.create_hooks(CONFIG_DEFAULT)
        self.hooks.subordinate_register(
            mongo='mongodb://tabby:miaow@home.ch:27017/mydb',
            rabbit='the_rabbit_connection')
        assert_equal(self.hooks.local_config.api_nat_socket, '')
        celeryconfig = {}
        execfile(self.hooks.local_config.celery_config_file, celeryconfig)
        assert_equal(celeryconfig['BROKER_URL'], 'the_rabbit_connection')
        assert_equal(celeryconfig['CELERY_MONGODB_BACKEND_SETTINGS'], {
            'host': 'home.ch', 'port': '27017', 'user': 'tabby', 'password': 'miaow',
            'database': 'mydb', 'taskmeta_collection': 'taskmeta'})
        assert_equal(celeryconfig['CELERYD_CONCURRENCY'], self.hooks.config.concurrency)

    def test_subordinate_register_transform(self):
        self.hooks = self.create_hooks(CONFIG_TRANSFORM)
        self.hooks.local_config.celery_template_file = os.path.join(
            '../oscied-transform', self.hooks.local_config.celery_template_file)
        self.hooks.subordinate_register(mongo='fail', rabbit='fail')
        assert_equal(self.hooks.local_config.api_nat_socket, CONFIG_TRANSFORM['api_nat_socket'])
        celeryconfig = {}
        execfile(self.hooks.local_config.celery_config_file, celeryconfig)
        assert_equal(celeryconfig['BROKER_URL'], CONFIG_TRANSFORM['rabbit_connection'])
        assert_equal(celeryconfig['CELERY_MONGODB_BACKEND_SETTINGS'], {
            'host': 'home.ch', 'port': '27017', 'user': 'tabby', 'password': 'miaow',
            'database': 'mydb', 'taskmeta_collection': 'taskmeta'})
        assert_equal(celeryconfig['CELERYD_CONCURRENCY'], CONFIG_TRANSFORM['concurrency'])

if __name__ == '__main__':
    import nose
    nose.runmodule(argv=[__file__], exit=False)
