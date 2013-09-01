#!/usr/bin/env python
# -*- coding: utf-8 -*-

#**********************************************************************************************************************#
#              OPEN-SOURCE CLOUD INFRASTRUCTURE FOR ENCODING AND DISTRIBUTION : SCENARIOS
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
#
# Retrieved from https://github.com/ebu/OSCIED

import pygal, shutil, time
from os.path import join, dirname
#from requests.exceptions import ConnectionError
from library.oscied_lib.oscied_juju import OsciedEnvironment
from library.oscied_lib.pyutils.py_console import confirm #, print_error
from library.oscied_lib.pyutils.py_datetime import datetime_now
#from library.oscied_lib.pyutils.py_filesystem import try_remove
from library.oscied_lib.pyutils.py_juju import DeploymentScenario
#from library.oscied_lib.pyutils.py_serialization import json2object, object2json
from library.oscied_lib.pyutils.py_unicode import configure_unicode
from library.oscied_lib.pyutils.py_collections import pygal_deque

description = u'Launch IBC 2013 demo setup (MaaS Cluster with 3 machines // Amazon)'

FAST = True
TIME_SCALE = 70
SCENARIO_PATH = dirname(__file__)

CONFIG_AMAZ = join(SCENARIO_PATH, u'config_amazon.yaml')
CONFIG_MAAS = join(SCENARIO_PATH, u'config_maas.yaml')

STATS_AMAZ = {u'oscied-transform': pygal_deque(maxlen=TIME_SCALE), u'oscied-publisher': pygal_deque(maxlen=TIME_SCALE)}
STATS_MAAS = {u'oscied-transform': pygal_deque(maxlen=TIME_SCALE), u'oscied-publisher': pygal_deque(maxlen=TIME_SCALE)}

EVENTS_AMAZ = {
     0: {u'oscied-transform': 5, u'oscied-publisher': 0},
    17: {u'oscied-transform': 0},
    43: {u'oscied-publisher': 1},
    45: {u'oscied-transform': 4},
    50: {u'oscied-publisher': 3},
    55: {u'oscied-publisher': 1}
}
EVENTS_MAAS = {
     0: {u'oscied-transform': 4, u'oscied-publisher': 2},
}


class IBC2013(DeploymentScenario):

    def run(self):
        print(description)
        if confirm(u'Deploy on MAAS'):
            self.deploy_maas()
        if confirm(u'Initialize orchestra on MAAS'):
            self.maas.init_api(SCENARIO_PATH, flush=True)
        if confirm(u'Deploy on Amazon'):
            self.deploy_amazon()
        if confirm(u'Initialize orchestra on Amazon'):
            self.amazon.init_api(SCENARIO_PATH, flush=True)
        if confirm(u'Start events loop'):
            self.events_loop()

    def deploy_maas(self):
        self.maas.bootstrap(wait_started=True, timeout=1200, polling_delay=30)
        self.maas.deploy(u'oscied-storage',   u'oscied-storage',   local=True, num_units=4, expose=True) # 1,2,3
        # WAIT
        self.maas.deploy(u'oscied-orchestra', u'oscied-orchestra', local=True, to=1, expose=True)
        # WAIT
        self.maas.deploy(u'oscied-webui',     u'oscied-webui',     local=True, to=1, expose=True)
        self.maas.deploy(u'oscied-publisher', u'oscied-publisher', local=True, to=2, expose=True)
        self.maas.deploy(u'oscied-publisher', u'oscied-publisher', local=True, to=3, expose=True) #3=5
        # WAIT
        self.maas.deploy(u'oscied-transform', u'oscied-transform', local=True, to=1)
        self.maas.deploy(u'oscied-transform', u'oscied-transform', local=True, to=2)
        self.maas.deploy(u'oscied-transform', u'oscied-transform', local=True, to=3) #3=5
        # WAIT -> Makes juju crazy (/var/log/juju/all-machines.log -> growing to GB)
        self.maas.deploy(u'oscied-storage',   u'oscied-storage',   local=True, to=0, expose=True)
        # WAIT -> Makes juju crazy (/var/log/juju/all-machines.log -> growing to GB)
        self.maas.deploy(u'oscied-transform', u'oscied-transform', local=True, to=0, expose=True)

        if confirm(u'Disconnect all services [DEBUG PURPOSE ONLY] (with juju remove-relation)'):
            for peer in (u'orchestra', u'webui', u'transform', u'publisher'):
                self.maas.remove_relation(u'oscied-storage', u'oscied-{0}'.format(peer))
            self.maas.remove_relation(u'oscied-orchestra:api', u'oscied-webui:api')
            self.maas.remove_relation(u'oscied-orchestra:transform', u'oscied-transform:transform')
            self.maas.remove_relation(u'oscied-orchestra:publisher', u'oscied-publisher:publisher')

        for peer in (u'orchestra', u'webui', u'transform', u'publisher'):
            self.maas.add_relation(u'oscied-storage', u'oscied-{0}'.format(peer))
        self.maas.add_relation(u'oscied-orchestra:api', u'oscied-webui:api')
        self.maas.add_relation(u'oscied-orchestra:transform', u'oscied-transform:transform')
        self.maas.add_relation(u'oscied-orchestra:publisher', u'oscied-publisher:publisher')

    def deploy_amazon(self):
        self.amazon.bootstrap(wait_started=True)
        self.amazon.deploy(u'oscied-transform', u'oscied-transform', local=True,
                           constraints=u'arch=amd64 cpu-cores=4 mem=1G')
        self.amazon.deploy(u'oscied-publisher', u'oscied-publisher', local=True, expose=True)
        self.amazon.deploy(u'oscied-orchestra', u'oscied-orchestra', local=True, expose=True)
        # WAIT
        self.amazon.deploy(u'oscied-storage',   u'oscied-storage',   local=True, to=3)
        self.amazon.deploy(u'oscied-webui',     u'oscied-webui',     local=True, to=3, expose=True)
        for peer in (u'orchestra', u'webui', u'transform', u'publisher'):
            self.amazon.add_relation(u'oscied-storage', u'oscied-{0}'.format(peer))
        self.amazon.add_relation(u'oscied-orchestra:transform', u'oscied-transform:transform')
        self.amazon.add_relation(u'oscied-orchestra:publisher', u'oscied-publisher:publisher')
        self.amazon.add_relation(u'oscied-orchestra:api',       u'oscied-webui:api')

    def events_loop(self):
        #if os.path.exists(u'statistics.json'):
        #    with open(u'statistics.json', u'r', u'utf-8') as f:
        #        self.statistics = json2object(f.read())
        #else:
        #self.environment = u'amazon'
        #try:
        #    client = self.get_client()
        #    print(client.about)
        #except (ConnectionError, RuntimeError) as e:
        #    print_error(u'Unable to connect to API, reason: {0}'.format(e), exit_code=None)
        #    # FIXME exit_code=1 in production !!!
        # print(u'Flush the database')
        # print(client.flush())
        #print(u'Register an administrator')
        #admin = User(first_name=u'Admin', last_name=u'Demo', mail=u'admin.demo@oscied.org',
        #             secret='big_secret_to_sav3', admin_platform=True)
        #admin = client.login_or_add(admin, self.root) # FIXME enable that in production !!!

        old_index = None
        while True:
            # Get current time to retrieve state
            now = datetime_now(format=None)
            index = now.second if FAST else now.minute
            if index != old_index:
                old_index = index
                self.handle_event(index)
            else:
                print(u'Skip already consumed event(s) for minute {0}.'.format(index))
            now = datetime_now(format=None)
            sleep_time = 0.8 if FAST else 60 - now.second
            print(u'Sleep {0} seconds ...'.format(sleep_time))
            time.sleep(sleep_time)
        #try:
        #    with open(u'statistics.json.tmp', u'w', u'utf-8') as f:
        #        f.write(object2json(self.statistics))
        #    os.rename(u'statistics.json.tmp', u'statistics.json')
        #finally:
        #    try_remove(u'statistics.json.tmp')

    def handle_event(self, index):
        line_chart = pygal.Line(show_dots=True, truncate_legend=20)
        line_chart.title = u'OSCIED services (# of units)'
        for environment in self.environments:
            event = environment.events.get(index, {})
            print(u'Handle {0} scheduled event for minute {1} = {2}.'.format(environment.name, index, event))
            for service, history in environment.statistics.items():
                history.append(event.get(service, None))
                line_chart.add(u'{0} - {1}'.format(environment.name, service.replace(u'oscied-', u'')), history.list)
        line_chart.render_to_file(u'oscied.new.svg')
        shutil.copy(u'oscied.new.svg', u'oscied.svg')

if __name__ == u'__main__':
    configure_unicode()
    IBC2013().main(environments=[
        OsciedEnvironment(u'amazon', config=CONFIG_AMAZ, release=u'raring',  statistics=STATS_AMAZ, events=EVENTS_AMAZ),
        OsciedEnvironment(u'maas',   config=CONFIG_MAAS, release=u'precise', statistics=STATS_MAAS, events=EVENTS_MAAS)
    ])

# pie_chart = pygal.Pie()
# pie_chart.title = 'OSCIED  (in %)'
# pie_chart.add('IE', [5.7, 10.2, 2.6, 1])
# pie_chart.add('Firefox', [.6, 16.8, 7.4, 2.2, 1.2, 1, 1, 1.1, 4.3, 1])
# pie_chart.add('Chrome', [.3, .9, 17.1, 15.3, .6, .5, 1.6])
# pie_chart.add('Safari', [4.4, .1])
# pie_chart.add('Opera', [.1, 1.6, .1, .5])

# worldmap_chart = pygal.Worldmap()
# worldmap_chart.title = 'Where is OSCIED running ?'
# worldmap_chart.add('MAAS countries', {'nl': 4})
# worldmap_chart.add('Amazon countries', {'us': 6})
# worldmap_chart.render_to_file('world.svg')
