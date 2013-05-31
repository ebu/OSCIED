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
import pyutils.pyutils
from copy import copy
from mock import call
from nose.tools import assert_equal
from oscied_lib.CharmHooks import DEFAULT_OS_ENV
from oscied_lib.TransformConfig import TransformConfig
from oscied_lib.CharmHooks_Storage import CharmHooks_Storage
from pyutils.pyutils import mock_cmd, mock_side_effect

CONFIG_DEFAULT = {
    'storage_address': '', 'storage_nat_address': '', 'storage_fstype': '',
    'storage_mountpoint': '', 'storage_options': '', 'storage_path': 'test_path'
}

CONFIG_STORAGE = {
    'storage_address': 'home.ch', 'storage_nat_address': '', 'storage_fstype': 'glusterfs',
    'storage_mountpoint': 'medias_volume_0', 'storage_options': ''
}

CONFIG_STORAGE_NAT = {
    'storage_address': 'home.ch', 'storage_nat_address': 'proxy.ch', 'storage_fstype': 'glusterfs',
    'storage_mountpoint': 'medias_volume_0', 'storage_options': ''
}


OS_ENV = copy(DEFAULT_OS_ENV)
OS_ENV['JUJU_UNIT_NAME'] = 'oscied-transform/0'
RETURNS = []


class CharmHooks_Storage_tmp(CharmHooks_Storage):
    def __init__(self, m, c, o):
        super(CharmHooks_Storage_tmp, self).__init__(m, c, o)

    @property
    def storage_is_mounted(self):
        return mock_side_effect()


class TestCharmHooks_Storage(object):

    def create_hooks(self, hooks_class, default_config):
        hooks = hooks_class(None, default_config, OS_ENV)
        hooks.local_config = TransformConfig()
        hooks.local_config.storage_mount_sleep_delay = 0.01
        shutil.copy(hooks.local_config.hosts_file, 'hosts')
        system_hosts = open(hooks.local_config.hosts_file).readlines()
        hooks.local_config.hosts_file = 'hosts'  # Avoid writing to system hosts file !
        return hooks, system_hosts

    def tearDown(self):
        os.remove('hosts')

    def test_storage_remount_no_storage_at_all(self):
        self.hooks, system_hosts = self.create_hooks(CharmHooks_Storage, CONFIG_DEFAULT)
        self.hooks.cmd = mock_cmd()
        self.hooks.storage_remount()
        assert_equal(self.hooks.cmd.call_args_list, [])
        assert_equal(system_hosts, open(self.hooks.local_config.hosts_file).readlines())

    def test_storage_remount_storage_config_nat_hosts_updated(self):
        self.hooks, system_hosts = self.create_hooks(CharmHooks_Storage_tmp, CONFIG_STORAGE_NAT)
        self.hooks.cmd = mock_cmd()
        pyutils.pyutils.MOCK_SIDE_EFFECT_RETURNS = [False, False, True, True]
        self.hooks.storage_remount()
        assert_equal(self.hooks.cmd.call_args_list,
            [call(['mount', '-t', 'glusterfs', 'proxy.ch:/medias_volume_0', '/mnt/storage'])])
        assert('proxy.ch home.ch' in open(self.hooks.local_config.hosts_file).readlines()[-1])
        assert_equal(system_hosts, open(self.hooks.local_config.hosts_file).readlines()[:-1])

    def test_storage_remount_storage_config(self):
        self.hooks, system_hosts = self.create_hooks(CharmHooks_Storage_tmp, CONFIG_STORAGE)
        self.hooks.cmd = mock_cmd()
        pyutils.pyutils.MOCK_SIDE_EFFECT_RETURNS = [False, False, True, True]
        self.hooks.storage_remount()
        assert_equal(self.hooks.cmd.call_args_list,
            [call(['mount', '-t', 'glusterfs', 'home.ch:/medias_volume_0', '/mnt/storage'])])
        assert_equal(system_hosts, open(self.hooks.local_config.hosts_file).readlines())

    def test_storage_remount_storage_config_do_not_re_re_mount(self):
        self.hooks, system_hosts = self.create_hooks(CharmHooks_Storage_tmp, CONFIG_STORAGE)
        self.hooks.cmd = mock_cmd()
        pyutils.pyutils.MOCK_SIDE_EFFECT_RETURNS = [False, False, True, True]
        self.hooks.storage_remount()
        pyutils.pyutils.MOCK_SIDE_EFFECT_RETURNS = [Exception('oups')]
        self.hooks.storage_remount()
        self.hooks.storage_remount()
        assert_equal(self.hooks.cmd.call_args_list,
            [call(['mount', '-t', 'glusterfs', 'home.ch:/medias_volume_0', '/mnt/storage'])])
        assert_equal(system_hosts, open(self.hooks.local_config.hosts_file).readlines())

    def test_storage_remount_do_not_re_re_mount(self):
        self.hooks, system_hosts = self.create_hooks(CharmHooks_Storage_tmp, CONFIG_DEFAULT)
        self.hooks.cmd = mock_cmd()
        pyutils.pyutils.MOCK_SIDE_EFFECT_RETURNS = [False, False, True, True]
        self.hooks.storage_remount(address='home.ch', fstype='glusterfs', mountpoint='my_vol_0')
        pyutils.pyutils.MOCK_SIDE_EFFECT_RETURNS = [Exception('oups')]
        self.hooks.storage_remount(address='home.ch', fstype='glusterfs', mountpoint='my_vol_0')
        self.hooks.storage_remount(address='home.ch', fstype='glusterfs', mountpoint='my_vol_0')
        assert_equal(self.hooks.cmd.call_args_list,
            [call(['mount', '-t', 'glusterfs', 'home.ch:/my_vol_0', '/mnt/storage'])])
        assert_equal(system_hosts, open(self.hooks.local_config.hosts_file).readlines())

if __name__ == '__main__':
    import nose
    nose.runmodule(argv=[__file__], exit=False)
