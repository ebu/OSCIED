#!/usr/bin/env python
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

import os, sys
from os.path import abspath, dirname
sys.path.append(abspath(dirname(dirname(__file__))))

import shutil
import oscied_lib.pyutils.py_unittest
from codecs import open
from copy import copy
from mock import call
from nose.tools import assert_equal
from oscied_lib.pyutils.py_unittest import mock_cmd, mock_side_effect
from oscied_lib.oscied_config import TransformLocalConfig
from oscied_lib.oscied_hook_base import CharmHooks_Storage, DEFAULT_OS_ENV

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
    def __init__(self, m, c, o):
        super(CharmHooks_Storage_tmp, self).__init__(m, c, o)

    @property
    def storage_is_mounted(self):
        return mock_side_effect()


class TestCharmHooks_Storage(object):

    def create_hooks(self, hooks_class, default_config):
        hooks = hooks_class(None, default_config, OS_ENV)
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
        oscied_lib.pyutils.py_unittest.MOCK_SIDE_EFFECT_RETURNS = [False, False, True, True]
        self.hooks.storage_remount()
        assert_equal(self.hooks.cmd.call_args_list,
            [call([u'mount', u'-t', u'glusterfs', u'proxy.ch:/medias_volume_0', u'/mnt/storage'])])
        assert(u'proxy.ch home.ch' in open(self.hooks.local_config.hosts_file, u'r', u'utf-8').readlines()[-1])
        assert_equal(system_hosts, open(self.hooks.local_config.hosts_file, u'r', u'utf-8').readlines()[:-1])

    def test_storage_remount_storage_config(self):
        self.hooks, system_hosts = self.create_hooks(CharmHooks_Storage_tmp, CONFIG_STORAGE)
        self.hooks.cmd = mock_cmd()
        oscied_lib.pyutils.py_unittest.MOCK_SIDE_EFFECT_RETURNS = [False, False, True, True]
        self.hooks.storage_remount()
        assert_equal(self.hooks.cmd.call_args_list,
            [call([u'mount', u'-t', u'glusterfs', u'home.ch:/medias_volume_0', u'/mnt/storage'])])
        assert_equal(system_hosts, open(self.hooks.local_config.hosts_file, u'r', u'utf-8').readlines())

    def test_storage_remount_storage_config_do_not_re_re_mount(self):
        self.hooks, system_hosts = self.create_hooks(CharmHooks_Storage_tmp, CONFIG_STORAGE)
        self.hooks.cmd = mock_cmd()
        oscied_lib.pyutils.py_unittest.MOCK_SIDE_EFFECT_RETURNS = [False, False, True, True]
        self.hooks.storage_remount()
        oscied_lib.pyutils.py_unittest.MOCK_SIDE_EFFECT_RETURNS = [Exception(u'oups')]
        self.hooks.storage_remount()
        self.hooks.storage_remount()
        assert_equal(self.hooks.cmd.call_args_list,
            [call([u'mount', u'-t', u'glusterfs', u'home.ch:/medias_volume_0', u'/mnt/storage'])])
        assert_equal(system_hosts, open(self.hooks.local_config.hosts_file, u'r', u'utf-8').readlines())

    def test_storage_remount_do_not_re_re_mount(self):
        self.hooks, system_hosts = self.create_hooks(CharmHooks_Storage_tmp, CONFIG_DEFAULT)
        self.hooks.cmd = mock_cmd()
        oscied_lib.pyutils.py_unittest.MOCK_SIDE_EFFECT_RETURNS = [False, False, True, True]
        self.hooks.storage_remount(address=u'home.ch', fstype=u'glusterfs', mountpoint=u'my_vol_0')
        oscied_lib.pyutils.py_unittest.MOCK_SIDE_EFFECT_RETURNS = [Exception(u'oups')]
        self.hooks.storage_remount(address=u'home.ch', fstype=u'glusterfs', mountpoint=u'my_vol_0')
        self.hooks.storage_remount(address=u'home.ch', fstype=u'glusterfs', mountpoint=u'my_vol_0')
        assert_equal(self.hooks.cmd.call_args_list,
            [call([u'mount', u'-t', u'glusterfs', u'home.ch:/my_vol_0', u'/mnt/storage'])])
        assert_equal(system_hosts, open(self.hooks.local_config.hosts_file, u'r', u'utf-8').readlines())

if __name__ == u'__main__':
    import nose
    nose.runmodule(argv=[__file__], exit=False)
