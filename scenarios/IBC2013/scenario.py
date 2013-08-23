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

from os.path import join, dirname
from library.oscied_lib.pyutils.py_console import confirm
from library.oscied_lib.pyutils.py_juju import DeploymentScenario

description = u'Launch IBC 2013 demo setup (MaaS Cluster with 3 machines // Amazon)'

class IBC2013(DeploymentScenario):

    def run(self):
        print(description)
        if confirm(u'Deploy on MAAS'):
            self.run_maas()
        if confirm(u'Deploy on Amazon'):
            self.run_amazon()

    def run_maas(self):
        self.config = join(dirname(__file__), u'config_maas.yaml')
        self.bootstrap(u'maas', wait_started=True)
        self.deploy(u'oscied-storage',   2,       expose=True)
        self.deploy(u'oscied-orchestra', 1, to=0, expose=True)
        self.deploy(u'oscied-webui',     1, to=0, expose=True)
        #self.deploy(u'oscied-transform', 1, to=1, u'oscied-transform1')
        #self.deploy(u'oscied-transform', 1, to=2, u'oscied-transform2')
        #self.deploy(u'oscied-publisher', 1, to=1, u'oscied-publisher1', expose=True)
        #self.deploy(u'oscied-publisher', 1, to=2, u'oscied-publisher2', expose=True)

        if confirm(u'Disconnect all services [DEBUG PURPOSE ONLY] (with juju remove-relation)'):
            for peer in (u'orchestra', u'webui', u'transform1', u'transform2', u'publisher1', u'publisher2'):
                self.remove_relation(u'oscied-storage', u'oscied-{0}'.format(peer))
            self.remove_relation(u'oscied-orchestra:api', u'oscied-webui:api')
            self.remove_relation(u'oscied-orchestra:transform', u'oscied-transform1:transform')
            self.remove_relation(u'oscied-orchestra:transform', u'oscied-transform2:transform')
            self.remove_relation(u'oscied-orchestra:publisher', u'oscied-publisher1:publisher')
            self.remove_relation(u'oscied-orchestra:publisher', u'oscied-publisher2:publisher')

        for peer in (u'orchestra', u'webui', u'transform1', u'transform2', u'publisher1', u'publisher2'):
            self.add_relation(u'oscied-storage', u'oscied-{0}'.format(peer))
        print(u'Orchestra relation with the web user interface')
        self.add_relation(u'oscied-orchestra:api', u'oscied-webui:api')
        print(u'Orchestra relation with transformation units')
        self.add_relation(u'oscied-orchestra:transform', u'oscied-transform1:transform')
        self.add_relation(u'oscied-orchestra:transform', u'oscied-transform2:transform')
        print(u'Orchestra relation with publication units')
        self.add_relation(u'oscied-orchestra:publisher', u'oscied-publisher1:publisher')
        self.add_relation(u'oscied-orchestra:publisher', u'oscied-publisher2:publisher')

    def run_amazon(self):
        # FIXME use --constraints "arch=amd64 cpu-cores=2 mem=1G"
        self.config = join(dirname(__file__), u'config_amazon.yaml')
        self.bootstrap(u'amazon', wait_started=True)
        self.deploy(u'oscied-orchestra', 1, local=True, expose=True)
        self.deploy(u'oscied-storage',   1, local=True)
        self.deploy(u'oscied-webui',     1, local=True, to=1, expose=True)
        self.deploy(u'oscied-transform', 1, local=True, to=2)
        self.deploy(u'oscied-publisher', 1, local=True, to=2, expose=True)
        has_proxy = self.deploy(u'haproxy', release=u'precise', expose=True, required=False)[0]
        for peer in (u'orchestra', u'webui', u'transform', u'publisher'):
            self.add_relation(u'oscied-storage', u'oscied-{0}'.format(peer))
        self.add_relation(u'oscied-orchestra:transform', u'oscied-transform:transform')
        self.add_relation(u'oscied-orchestra:publisher', u'oscied-publisher:publisher')
        self.add_relation(u'oscied-orchestra:api',       u'oscied-webui:api')
        if has_proxy:
            if self.add_relation(u'haproxy', u'oscied-webui'):
                self.unexpose_service(u'oscied-webui')

if __name__ == u'__main__':
    IBC2013().main()
