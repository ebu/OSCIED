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

import os, shutil
from codecs import open
from copy import copy
from mock import call
from nose.tools import assert_equal
import pytoolbox.unittest as py_unittest
from pytoolbox.juju import DEFAULT_OS_ENV
from pytoolbox.unittest import mock_cmd, mock_side_effect
from oscied_lib.config import TransformLocalConfig
from oscied_lib.hooks_base import CharmHooks_Storage

CONFIG_DEFAULT = {
    u'storage_address': u'', u'storage_nat_address': u'', u'storage_fstype': u'', u'storage_mountpoint': u'',
    u'storage_options': u'', u'storage_path': u'test_path'
}

CONFIG_STORAGE = {
    u'storage_address': u'home.ch', u'storage_nat_address': u'', u'storage_fstype': u'glusterfs',
    u'storage_mountpoint': u'medias_volume_0', u'storage_options': u''
}

CONFIG_STORAGE_NAT = {
    u'storage_address': u'home.ch', u'storage_nat_address': u'proxy.ch', u'storage_fstype': u'glusterfs',
    u'storage_mountpoint': u'medias_volume_0', u'storage_options': u''
}


OS_ENV, RETURNS = copy(DEFAULT_OS_ENV), []
OS_ENV[u'JUJU_UNIT_NAME'] = u'oscied-transform/0'


class CharmHooks_Storage_tmp(CharmHooks_Storage):
    def __init__(self, m, c, o, f, s):
        super(CharmHooks_Storage_tmp, self).__init__(m, c, o, f, s)

    @property
    def storage_is_mounted(self):
        return mock_side_effect()


class TestCharmHooks_Storage(object):

    def create_hooks(self, hooks_class, default_config):
        hooks = hooks_class(None, default_config, OS_ENV, u'test.json', TransformLocalConfig)
        hooks.local_config = TransformLocalConfig()
        hooks.local_config.storage_mount_sleep_delay = 0.01
        shutil.copy(hooks.local_config.hosts_file, u'hosts')
        system_hosts = open(hooks.local_config.hosts_file, u'r', u'utf-8').readlines()
        hooks.local_config.hosts_file = u'hosts'  # Avoid writing to system hosts file !
        return hooks, system_hosts

    def tearDown(self):
        os.remove(u'hosts')

    def test_storage_remount_no_storage_at_all(self):
        self.hooks, system_hosts = self.create_hooks(CharmHooks_Storage, CONFIG_DEFAULT)
        self.hooks.cmd = mock_cmd()
        self.hooks.storage_remount()
        assert_equal(self.hooks.cmd.call_args_list, [])
        assert_equal(system_hosts, open(self.hooks.local_config.hosts_file, u'r', u'utf-8').readlines())

    def test_storage_remount_storage_config_nat_hosts_updated(self):
        self.hooks, system_hosts = self.create_hooks(CharmHooks_Storage_tmp, CONFIG_STORAGE_NAT)
        self.hooks.cmd = mock_cmd()
        py_unittest.MOCK_SIDE_EFFECT_RETURNS = [False, False, True, True]
        self.hooks.storage_remount()
        assert_equal(self.hooks.cmd.call_args_list,
            [call([u'mount', u'-t', u'glusterfs', u'proxy.ch:/medias_volume_0', u'/mnt/storage'])])
        assert(u'proxy.ch home.ch' in open(self.hooks.local_config.hosts_file, u'r', u'utf-8').readlines()[-1])
        assert_equal(system_hosts, open(self.hooks.local_config.hosts_file, u'r', u'utf-8').readlines()[:-1])

    def test_storage_remount_storage_config(self):
        self.hooks, system_hosts = self.create_hooks(CharmHooks_Storage_tmp, CONFIG_STORAGE)
        self.hooks.cmd = mock_cmd()
        py_unittest.MOCK_SIDE_EFFECT_RETURNS = [False, False, True, True]
        self.hooks.storage_remount()
        assert_equal(self.hooks.cmd.call_args_list,
            [call([u'mount', u'-t', u'glusterfs', u'home.ch:/medias_volume_0', u'/mnt/storage'])])
        assert_equal(system_hosts, open(self.hooks.local_config.hosts_file, u'r', u'utf-8').readlines())

    def test_storage_remount_storage_config_do_not_re_re_mount(self):
        self.hooks, system_hosts = self.create_hooks(CharmHooks_Storage_tmp, CONFIG_STORAGE)
        self.hooks.cmd = mock_cmd()
        py_unittest.MOCK_SIDE_EFFECT_RETURNS = [False, False, True, True]
        self.hooks.storage_remount()
        py_unittest.MOCK_SIDE_EFFECT_RETURNS = [Exception(u'oups')]
        self.hooks.storage_remount()
        self.hooks.storage_remount()
        assert_equal(self.hooks.cmd.call_args_list,
            [call([u'mount', u'-t', u'glusterfs', u'home.ch:/medias_volume_0', u'/mnt/storage'])])
        assert_equal(system_hosts, open(self.hooks.local_config.hosts_file, u'r', u'utf-8').readlines())

    def test_storage_remount_do_not_re_re_mount(self):
        self.hooks, system_hosts = self.create_hooks(CharmHooks_Storage_tmp, CONFIG_DEFAULT)
        self.hooks.cmd = mock_cmd()
        py_unittest.MOCK_SIDE_EFFECT_RETURNS = [False, False, True, True]
        self.hooks.storage_remount(address=u'home.ch', fstype=u'glusterfs', mountpoint=u'my_vol_0')
        py_unittest.MOCK_SIDE_EFFECT_RETURNS = [Exception(u'oups')]
        self.hooks.storage_remount(address=u'home.ch', fstype=u'glusterfs', mountpoint=u'my_vol_0')
        self.hooks.storage_remount(address=u'home.ch', fstype=u'glusterfs', mountpoint=u'my_vol_0')
        assert_equal(self.hooks.cmd.call_args_list,
            [call([u'mount', u'-t', u'glusterfs', u'home.ch:/my_vol_0', u'/mnt/storage'])])
        assert_equal(system_hosts, open(self.hooks.local_config.hosts_file, u'r', u'utf-8').readlines())
