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

import CharmHooks
from StorageHooks import StorageHooks

CONFIG = {'verbose': False, 'replica_count': 1}

INFOS_STDOUT = ('\nVolume Name: medias_volume_14\nType: Distribute\nStatus: Started'
                '\nNumber of Bricks: 1\nTransport-type: tcp\nBricks:'
                '\nBrick1: ip-10-36-122-169.ec2.internal:/exp14\n')
INFOS_DICT = {'name': 'medias_volume_14', 'type': 'Distribute', 'status': 'Started',
              'transport': 'tcp', 'bricks': ['ip-10-36-122-169.ec2.internal:/exp14']}


class TestStorageHooks(object):

    def volume_do(self, action, volume=None, options='', input=None, cli_input=None, fail=True):
        if action == 'info':
            return {'stdout': INFOS_STDOUT, 'stderr': None, 'returncode': 0}
        return None

    def test_volume_infos(self):
        hooks = StorageHooks(None, CONFIG, CharmHooks.DEFAULT_OS_ENV)
        hooks.volume_do = self.volume_do  # Replace volume_do by something without gluster
        infos = hooks.volume_infos()
        assert(infos == INFOS_DICT)
