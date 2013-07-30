#!/usr/bin/env python2
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
from os.path import abspath, dirname, join
sys.path.append(abspath(dirname(dirname(__file__))))
sys.path.append(abspath(join(dirname(dirname(__file__)), u'pyutils')))

from copy import copy
from mock import call
from nose.tools import assert_equal, raises
from pyutils.py_mock import mock_cmd
from oscied_lib.CharmHooks import DEFAULT_OS_ENV
from oscied_lib.StorageConfig import StorageConfig
from oscied_lib.StorageHooks import StorageHooks

CONFIG = {u'verbose': False, u'replica_count': 1, u'allowed_ips': u'*'}
OS_ENV, RETURNS = copy(DEFAULT_OS_ENV), []
OS_ENV[u'JUJU_UNIT_NAME'] = u'oscied-storage/14'


class TestStorageHooks(object):
    #return {'stdout': INFOS_STDOUT, 'stderr': None, 'returncode': 0}

    def setUp(self):
        StorageConfig().write(u'test.pkl')
        self.hooks = StorageHooks(None, CONFIG, u'test.pkl', OS_ENV)

    def tearDown(self):
        os.remove(u'test.pkl')

    def test_volume_set_allowed_ips_ok(self):
        self.hooks.config.allowed_ips = u'192.168.1.*,10.10.*'
        self.hooks.local_config.allowed_ips = [u'129.194.185.47']
        self.hooks.volume_do = mock_cmd(
            u'\nVolume Name: medias_volume_14\nType: Distribute\nStatus: Started\nNumber of Bricks: 1\n'
            'Transport-type: tcp\nBricks:\nBrick1: ip-10-36-122-169.ec2.internal:/exp14\n'
            'Options Reconfigured:\nauth.allow: 10.10.*,129.194.185.47,192.168.1.*\n')
        self.hooks.volume_set_allowed_ips()
        assert_equal(self.hooks.volume_do.call_args_list, [
            call(u'set', fail=False, volume=u'medias_volume_14',
                 options=u'auth.allow "10.10.*,129.194.185.47,192.168.1.*"'),
            call(u'info', fail=False, volume=u'medias_volume_14'),
            call(u'info', fail=False, volume=u'medias_volume_14')])

    @raises(ValueError)
    def test_volume_set_allowed_ips_raise(self):
        self.hooks.config.allowed_ips = u'192.168.1.*,10.10.*'
        self.hooks.local_config.allowed_ips = [u'129.194.185.47']
        self.hooks.volume_do = mock_cmd(
            u'\nVolume Name: medias_volume_14\nType: Distribute\nStatus: Started\nNumber of Bricks: 1\n'
            'Transport-type: tcp\nBricks:\nBrick1: ip-10-36-122-169.ec2.internal:/exp14\n'
            'Options Reconfigured:\nauth.allow: 192.168.1.*\n')
        self.hooks.volume_set_allowed_ips()

    def test_volume_infos(self):
        self.hooks.volume_do = mock_cmd(
            u'\nVolume Name: medias_volume_14\nType: Distribute\nStatus: Started\nNumber of Bricks: 1\n'
            'Transport-type: tcp\nBricks:\nBrick1: ip-10-36-122-169.ec2.internal:/exp14\n'
            'Options Reconfigured:\nauth.allow: 192.168.0.104\n')
        infos = self.hooks.volume_infos()
        assert_equal(infos, {
            u'name': u'medias_volume_14', u'type': u'Distribute', u'status': u'Started', u'transport': u'tcp',
            u'bricks': [u'ip-10-36-122-169.ec2.internal:/exp14'], u'auth_allow': u'192.168.0.104'})
        self.hooks.volume_do.assert_called_with(u'info', volume=None, fail=False)

    # def test_install_replica_1_with_client(self):
    #     self.hooks.local_config.allowed_ips = ''

    #     pyutils.pyutils.MOCK_SIDE_EFFECT_RETURNS = [
    #         '', '', '',  # apt-get
    #         '', '',  # volume_create_or_expand
    #         {'stdout': '\nVolume Name: medias_volume_14\nType: Distribute\nStatus: Started'
    #         '\nNumber of Bricks: 1\nTransport-type: tcp\nBricks:'
    #         '\nBrick1: 10.1.1.10:/exp14\n'}, {'stdout': ''}]

    #     self.hooks.private_address = '10.1.1.10'
    #     self.hooks.hook_uninstall = Mock(return_value=None)
    #     self.hooks.cmd = Mock(side_effect=mock_side_effect)
    #     self.hooks.volume_set_allowed_ips = Mock(return_value=None)
    #     self.hooks.trigger(hook_name='install')
    #     self.hooks.volume_set_allowed_ips.assert_called_once()
    #     assert_equal(self.hooks.cmd.call_args_list, [
    #         call('apt-get -y install ntp glusterfs-server nfs-common'),
    #         call('apt-get -y upgrade'),
    #         call('service ntp restart'),
    #         call('gluster volume create medias_volume_14  10.1.1.10:/exp14', fail=True, input=None, cli_input=None),
    #         call('gluster volume start medias_volume_14 ', fail=True, input=None, cli_input=None),
    #         call('gluster volume info medias_volume_14 ', fail=False, input=None, cli_input=None),
    #         call('gluster volume rebalance medias_volume_14 status', fail=False, input=None, cli_input=None)])

    #     self.hooks.relation_set = Mock(return_value=None)
    #     self.hooks.relation_get = Mock(return_value='129.194.185.47')
    #     self.hooks.trigger(hook_name='storage_relation_joined')
    #     self.hooks.relation_set.assert_called_with(mountpoint='medias_volume_14', options='', fstype='glusterfs')
    #     self.hooks.relation_get.assert_called_with('private-address')
    #     assert_equal(self.hooks.local_config.allowed_ips, '129.194.185.47')

    #     self.hooks.relation_set = Mock(return_value=None)
    #     self.hooks.relation_get = Mock(return_value='129.194.185.50')
    #     self.hooks.trigger(hook_name='storage_relation_joined')
    #     self.hooks.relation_set.assert_called_with(mountpoint='medias_volume_14', options='', fstype='glusterfs')
    #     self.hooks.relation_get.assert_called_with('private-address')
    #     assert_equal(self.hooks.local_config.allowed_ips, '129.194.185.47,129.194.185.50')

    #     pyutils.pyutils.MOCK_SIDE_EFFECT_RETURNS = [
    #         '10.1.1.11', '10.1.1.11',  # peer-relation changed loop
    #         'FIXME TODO',  # volume_create_or_expand
    #         ]
    #     self.hooks.relation_get = Mock(side_effect=mock_side_effect)
    #     self.hooks.relation_list = Mock(return_value=['cui-cui'])
    #     self.hooks.peer_probe = Mock(return_value=None)
    #     self.hooks.trigger(hook_name='peer_relation_joined')
    #     self.hooks.trigger(hook_name='peer_relation_changed')

if __name__ == u'__main__':
    import nose
    nose.runmodule(argv=[__file__], exit=False)
