#!/usr/bin/env python
# -*- coding: utf-8 -*-

#**********************************************************************************************************************#
#              OPEN-SOURCE CLOUD INFRASTRUCTURE FOR ENCODING AND DISTRIBUTION : SCENARIOS
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

from oscied_lib.pyutils.py_juju import DeploymentScenario, unexpose_service

description = u'Launch oscied (minimal setup) locally (LXC provider)'

class Local(DeploymentScenario):

    def run(self):
        print(description)
        self.bootstrap('local', wait_started=True)
        self.deploy('oscied-orchestra', 1, expose=True)
        self.deploy('oscied-webui',     1, expose=True)
        self.deploy('oscied-storage',   1)
        self.deploy('oscied-transform', 1)
        self.deploy('oscied-publisher', 1, expose=True)
        has_proxy = self.deploy('haproxy', release='precise', expose=True, required=False)
        self.add_relation('oscied-storage',
                          ['oscied-transform', 'oscied-publisher', 'oscied-orchestra', 'oscied-webui'])
        self.add_relation('oscied-orchestra:transform', 'oscied-transform:transform')
        self.add_relation('oscied-orchestra:publisher', 'oscied-publisher:publisher')
        self.add_relation('oscied-orchestra:api', 'oscied-webui:api')
        if has_proxy:
            if self.add_relation('haproxy', 'oscied-webui'):
                unexpose_service('oscied-webui')

if __name__ == '__main__':
    Local().main()
