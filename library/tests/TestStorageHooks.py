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
from mock import call, Mock
from nose.tools import assert_equal, raises
from oscied_lib.pyutils.py_juju import DEFAULT_OS_ENV
import oscied_lib.pyutils.py_unittest as py_unittest
from oscied_lib.pyutils.py_unittest import mock_cmd, mock_side_effect
from oscied_lib.oscied_config import StorageLocalConfig
from oscied_lib.StorageHooks import StorageHooks

CONFIG = {u'verbose': False, u'replica_count': 1, u'allowed_ips': u'*', u'bricks_root_path': u'/mnt/somewhere'}
OS_ENV, RETURNS = copy(DEFAULT_OS_ENV), []
OS_ENV[u'JUJU_UNIT_NAME'] = u'oscied-storage/14'


class TestStorageHooks(object):
    #return {'stdout': INFOS_STDOUT, 'stderr': None, 'returncode': 0}

    def setUp(self):
        StorageLocalConfig().write(u'test.pkl')
        self.hooks = StorageHooks(None, CONFIG, u'test.pkl', OS_ENV)

    def tearDown(self):
        os.remove(u'test.pkl')

    def test_class_properties(self):
        assert_equal(self.hooks.brick(), u'{0}:/mnt/somewhere/bricks/exp14'.format(self.hooks.private_address))
        assert_equal(self.hooks.bricks_path, u'/mnt/somewhere/bricks')
        assert_equal(self.hooks.volume, u'medias_volume_14')

    def test_volume_set_allowed_ips_ok(self):
        self.hooks.config.allowed_ips = u'192.168.1.*,10.10.*'
        self.hooks.local_config.allowed_ips = [u'129.194.185.47']
        self.hooks.volume_do = mock_cmd(
            u'\nVolume Name: medias_volume_14\nType: Distribute\nStatus: Started\nNumber of Bricks: 1\n'
            'Transport-type: tcp\nBricks:\nBrick1: ip-10-36-122-169.ec2.internal:/mnt/bricks/exp14\n'
            'Options Reconfigured:\nauth.allow: 10.10.*,129.194.185.47,192.168.1.*\n')
        self.hooks.volume_set_allowed_ips()
        assert_equal(self.hooks.volume_do.call_args_list, [
            call(u'set', fail=False, volume=u'medias_volume_14',
                 options=u'auth.allow "10.10.*,129.194.185.47,192.168.1.*"'),
            call(u'info', fail=False, volume=u'medias_volume_14'),
            call(u'info', fail=False, volume=u'medias_volume_14')])
        assert_equal(self.hooks.allowed_ips_string, u'10.10.*,129.194.185.47,192.168.1.*')

    @raises(ValueError)
    def test_volume_set_allowed_ips_raise(self):
        self.hooks.config.allowed_ips = u'192.168.1.*,10.10.*'
        self.hooks.local_config.allowed_ips = [u'129.194.185.47']
        self.hooks.volume_do = mock_cmd(
            u'\nVolume Name: medias_volume_14\nType: Distribute\nStatus: Started\nNumber of Bricks: 1\n'
            'Transport-type: tcp\nBricks:\nBrick1: ip-10-36-122-169.ec2.internal:/mnt/bricks/exp14\n'
            'Options Reconfigured:\nauth.allow: 192.168.1.*\n')
        self.hooks.volume_set_allowed_ips()

    def test_volume_infos(self):
        self.hooks.volume_do = mock_cmd(
            u'\nVolume Name: medias_volume_14\nType: Distribute\nStatus: Started\nNumber of Bricks: 1\n'
            'Transport-type: tcp\nBricks:\nBrick1: ip-10-36-122-169.ec2.internal:/mnt/bricks/exp14\n'
            'Options Reconfigured:\nauth.allow: 192.168.0.104\n')
        infos = self.hooks.volume_infos()
        assert_equal(infos, {
            u'name': u'medias_volume_14', u'type': u'Distribute', u'status': u'Started', u'transport': u'tcp',
            u'bricks': [u'ip-10-36-122-169.ec2.internal:/mnt/bricks/exp14'], u'auth_allow': u'192.168.0.104'})
        self.hooks.volume_do.assert_called_with(u'info', volume=None, fail=False)

    def test_install_replica_1_with_client(self):
        self.hooks.local_config.allowed_ips = []

        py_unittest.MOCK_SIDE_EFFECT_RETURNS = [
            u'', u'', u'', u'',  # apt-get + ntp
            u'', u'',  # volume_create_or_expand
            {u'stdout': u'\nVolume Name: medias_volume_14\nType: Distribute\nStatus: Started'
            u'\nNumber of Bricks: 1\nTransport-type: tcp\nBricks:'
            u'\nBrick1: 10.1.1.10:/exp14\n'}, {'stdout': ''}]

        self.hooks.private_address = '10.1.1.10'
        self.hooks.hook_uninstall = Mock(return_value=None)
        self.hooks.cmd = Mock(side_effect=mock_side_effect)
        self.hooks.volume_set_allowed_ips = Mock(return_value=None)
        self.hooks.trigger(hook_name='install')
        self.hooks.volume_set_allowed_ips.assert_called_once()
        assert_equal(self.hooks.cmd.call_args_list, [
            call(u'apt-get -y update', fail=False),
            call(u'apt-get -y upgrade'),
            call(u'apt-get -y install ntp glusterfs-server nfs-common'),
            call(u'service ntp restart'),
            call(u'gluster volume create medias_volume_14  10.1.1.10:/mnt/somewhere/bricks/exp14', fail=True, input=None, cli_input=None),
            call(u'gluster volume start medias_volume_14 ', fail=True, input=None, cli_input=None),
            call(u'gluster volume info medias_volume_14 ', fail=False, input=None, cli_input=None),
            call(u'gluster volume rebalance medias_volume_14 status', fail=False, input=None, cli_input=None)])

        self.hooks.relation_set = Mock(return_value=None)
        self.hooks.relation_get = Mock(return_value=u'129.194.185.47')
        self.hooks.trigger(hook_name=u'storage_relation_joined')
        self.hooks.relation_set.assert_called_with(mountpoint=u'medias_volume_14', options=u'', fstype=u'glusterfs')
        self.hooks.relation_get.assert_called_with(u'private-address')
        assert_equal(self.hooks.local_config.allowed_ips, [u'129.194.185.47'])

        self.hooks.relation_set = Mock(return_value=None)
        self.hooks.relation_get = Mock(return_value=u'129.194.185.50')
        self.hooks.trigger(hook_name=u'storage_relation_joined')
        self.hooks.relation_set.assert_called_with(mountpoint=u'medias_volume_14', options=u'', fstype=u'glusterfs')
        self.hooks.relation_get.assert_called_with(u'private-address')
        assert_equal(self.hooks.local_config.allowed_ips, [u'129.194.185.47', u'129.194.185.50'])

        # FIXME unit test relation departed & co with known input values from a live test with juju to fix issue #66

        # py_unittest.MOCK_SIDE_EFFECT_RETURNS = [
        #     u'10.1.1.11', u'10.1.1.11',  # peer-relation changed loop
        #     u'FIXME TODO',  # volume_create_or_expand
        #     ]
        # self.hooks.relation_get = Mock(side_effect=mock_side_effect)
        # self.hooks.relation_list = Mock(return_value=[u'cui-cui'])
        # self.hooks.peer_probe = Mock(return_value=None)
        # self.hooks.trigger(hook_name=u'peer_relation_joined')
        # self.hooks.trigger(hook_name=u'peer_relation_changed')

if __name__ == u'__main__':
    import nose
    nose.runmodule(argv=[__file__], exit=False)
