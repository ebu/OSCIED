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
from os.path import abspath, dirname
sys.path.append(abspath(dirname(dirname(__file__))))

from copy import copy
from nose.tools import assert_equal
from oscied_lib.oscied_config import TransformLocalConfig
from oscied_lib.oscied_hook_base import DEFAULT_OS_ENV
from oscied_lib.TransformHooks import TransformHooks

CONFIG_DEFAULT = {
    u'verbose': False, u'concurrency': 1, u'rabbit_queues': u'transform_private', u'mongo_connection': u'',
    u'rabbit_connection': u'', u'api_nat_socket': u'', u'storage_address': u'', u'storage_nat_address': u'',
    u'storage_fstype': u'', u'storage_mountpoint': u'', u'storage_options': u''
}

CONFIG_TRANSFORM = {
    u'verbose': True, u'concurrency': 2, u'rabbit_queues': u'transform_other',
    u'mongo_connection': u'mongodb://tabby:miaow@home.ch:27017/mydb',
    u'rabbit_connection': u'another_rabbit_connection', u'api_nat_socket': u'the_nat_socket', u'storage_address': u'',
    u'storage_nat_address': u'', u'storage_fstype': u'', u'storage_mountpoint': u'', u'storage_options': u''
}

OS_ENV, RETURNS = copy(DEFAULT_OS_ENV), []
OS_ENV[u'JUJU_UNIT_NAME'] = u'oscied-transform/0'


class TestTransformHooks(object):

    def create_hooks(self, default_config):
        TransformLocalConfig().write(u'test.pkl')
        hooks = TransformHooks(None, default_config, u'test.pkl', OS_ENV)
        hooks.local_config.storage_mount_sleep_delay = 0.01
        hooks.local_config.hosts_file = u'hosts'  # Avoid writing to system hosts file !
        hooks.local_config.celery_config_file = u'celeryconfig.py'
        hooks.local_config.celery_template_file = os.path.join(
            u'../../charms/oscied-transform', hooks.local_config.celery_template_file)
        return hooks

    def tearDown(self):
        for f in (u'celeryconfig.py', u'hosts', u'test.pkl'):
            try:
                os.remove(f)
            except:
                pass

    def test_subordinate_register_default(self):
        self.hooks = self.create_hooks(CONFIG_DEFAULT)
        self.hooks.subordinate_register(mongo=u'mongodb://tabby:miaow@home.ch:27017/mydb',
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
            u'../../charms/oscied-transform', self.hooks.local_config.celery_template_file)
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
