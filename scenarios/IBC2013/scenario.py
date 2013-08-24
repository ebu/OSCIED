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

import time
from os.path import join, dirname
from requests.exceptions import ConnectionError
from library.oscied_lib.oscied_models import User
from library.oscied_lib.oscied_client import OrchestraAPIClient
from library.oscied_lib.pyutils.py_console import confirm, print_error
from library.oscied_lib.pyutils.py_datetime import datetime_now
from library.oscied_lib.pyutils.py_juju import DeploymentScenario
from library.oscied_lib.pyutils.py_unicode import configure_unicode

description = u'Launch IBC 2013 demo setup (MaaS Cluster with 3 machines // Amazon)'

CONFIG_AMAZON = join(dirname(__file__), u'config_amazon.yaml')
CONFIG_MAAS = join(dirname(__file__), u'config_maas.yaml')

FAST = True
POLLING_DELAY = 0.9 if FAST else 10
EVENTS_TIMETABLE = {
    # Amazon
     0: (u'oscied-transform', 4),
    17: (u'oscied-transform', 0),
    45: (u'oscied-transform', 2),
     0: (u'oscied-publisher', 0),
    43: (u'oscied-publisher', 1),
    50: (u'oscied-publisher', 2),
    55: (u'oscied-publisher', 1)
}

class IBC2013(DeploymentScenario):

    @property
    def root(self):
        return (u'root', self.root_secret)
    
    def get_parser(self, host='127.0.0.1', port=5000, root_secret=u'toto', **kwargs):
        # FIXME update menu.sh -> mandatory parameters ...
        # FIXME a toggle to disable argument parsing and use default (do not use positional params at all ?)
        parser = super(IBC2013, self).get_parser(**kwargs)
        parser.add_argument(u'host',        action=u'store', default=host)
        parser.add_argument(u'port',        action=u'store', default=port)
        parser.add_argument(u'root_secret', action=u'store', default=root_secret)
        return parser

    def run(self):
        print(description)
        if confirm(u'Deploy on MAAS'):
            self.deploy_maas()
        if confirm(u'Deploy on Amazon'):
            self.deploy_amazon()
        if confirm(u'Start events loop'):
            self.events_loop()

    def deploy_maas(self):
        self.config = CONFIG_MAAS
        self.bootstrap(u'maas', wait_started=True)
        self.deploy(u'oscied-storage',   u'oscied-storage',    local=True, num_units=2, expose=True)
        self.deploy(u'oscied-orchestra', u'oscied-orchestra',  local=True, to=0, expose=True)
        self.deploy(u'oscied-webui',     u'oscied-webui',      local=True, to=0, expose=True)
        self.deploy(u'oscied-transform', u'oscied-transform1', local=True, to=1)
        self.deploy(u'oscied-transform', u'oscied-transform2', local=True, to=2)
        self.deploy(u'oscied-publisher', u'oscied-publisher1', local=True, to=1, expose=True)
        self.deploy(u'oscied-publisher', u'oscied-publisher2', local=True, to=2, expose=True)

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

    def deploy_amazon(self):
        # FIXME use --constraints "arch=amd64 cpu-cores=2 mem=1G"
        self.config = CONFIG_AMAZON
        self.bootstrap(u'amazon', wait_started=True)
        self.deploy(u'oscied-orchestra', u'oscied-orchestra', local=True, expose=True)
        self.deploy(u'oscied-storage',   u'oscied-storage',   local=True)
        self.deploy(u'oscied-transform', u'oscied-transform', local=True, to=2)
        self.deploy(u'oscied-webui',     u'oscied-webui',     local=True, to=1, expose=True)
        self.deploy(u'oscied-publisher', u'oscied-publisher', local=True, to=2, expose=True)
        has_proxy = self.deploy(u'haproxy', u'haproxy', release=u'precise', expose=True, required=False)[0]
        for peer in (u'orchestra', u'webui', u'transform', u'publisher'):
            self.add_relation(u'oscied-storage', u'oscied-{0}'.format(peer))
        self.add_relation(u'oscied-orchestra:transform', u'oscied-transform:transform')
        self.add_relation(u'oscied-orchestra:publisher', u'oscied-publisher:publisher')
        self.add_relation(u'oscied-orchestra:api',       u'oscied-webui:api')
        if has_proxy:
            if self.add_relation(u'haproxy', u'oscied-webui'):
                self.unexpose_service(u'oscied-webui')

    def events_loop(self):
        client = OrchestraAPIClient(self.host, self.port, self.root)
        try:
            print(client.about)
        except ConnectionError as e:
            print_error(u'Unable to connect to API, reason: {0}'.format(e), exit_code=None)
            # FIXME exit_code=1 in production !!!
        # print(u'Flush the database')
        # print(client.flush())
        print(u'Register an administrator')
        admin = User(first_name=u'Admin', last_name=u'Demo', mail=u'admin.demo@oscied.org',
                     secret='big_secret_to_sav3', admin_platform=True)
        #admin = client.login_or_add(admin, self.root) # FIXME enable that in production !!!

        old_index = None
        while True:
            # Get current time to retrieve state
            now = datetime_now(format=None)
            index = now.second if FAST else now.minute
            if index != old_index:
                old_index = index
                event = EVENTS_TIMETABLE.get(index, None)
                if event:
                    self.handle_event(index, event)
                else:
                    print(u'No event scheduled for minute {0}.'.format(index))
            else:
                print(u'Skip already consumed event for minute {0}.'.format(index))
            print(u'Sleep {0} seconds ...'.format(POLLING_DELAY))
            time.sleep(POLLING_DELAY)

    def handle_event(self, index, event):
        print(u'Handle scheduled event for minute {0} = {1}.'.format(index, event))

if __name__ == u'__main__':
    from library.oscied_lib.pyutils.py_unicode import configure_unicode
    configure_unicode()
    IBC2013().main()
