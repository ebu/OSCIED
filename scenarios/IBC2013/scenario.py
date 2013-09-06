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

u"""
Entry-point of the demo scenario shown during the International Broadcasting Convention at RAI Amsterdam in 2013.

TODO

"""

# http://docs.mongodb.org/manual/reference/operator/
# file:///home/famille/David/git/OSCIED/scenarios/oscied_amazon.svg
# http://pygal.org/custom_styles/

import time
#from requests.exceptions import ConnectionError
from library.oscied_lib.oscied_models import User
from library.oscied_lib.oscied_juju import OsciedEnvironment
from library.oscied_lib.pyutils.py_console import confirm #, print_error
from library.oscied_lib.pyutils.py_datetime import datetime_now
#from library.oscied_lib.pyutils.py_filesystem import try_remove
from library.oscied_lib.pyutils.py_juju import DeploymentScenario, ERROR_STATES, PENDING_STATES, STARTED
from library.oscied_lib.pyutils.py_unicode import configure_unicode

from scenario_config import (
    ENABLE_TESTING, ENABLE_UNITS_API, CONFIG_AMAZ, CONFIG_MAAS, EVENTS_AMAZ, EVENTS_MAAS, LABELS, MAPPERS
)
from scenario_statistics import STATS_AMAZ, STATS_MAAS


description = u'Launch IBC 2013 demo setup (MaaS Cluster with 3 machines // Amazon)'

# def generate_line_chart(statistics_env,):
#     chart = pygal.Pie(width=width, height=height, explicit_size=explicit_size)
#     width=300, height=300, explicit_size=True, show_dots=True, truncate_legend=20


class IBC2013(DeploymentScenario):
    u"""
    The demo scenario's main class shown during the International Broadcasting Convention at RAI Amsterdam in 2013.

    TODO

    """
    def run(self):
        print(description)
        self.events_loop()
        # if confirm(u'Deploy on MAAS'):
        #     self.deploy_maas()
        # if confirm(u'Initialize orchestra on MAAS'):
        #     self.maas.init_api(SCENARIO_PATH, flush=True)
        # if confirm(u'Deploy on Amazon'):
        #     self.deploy_amazon()
        # if confirm(u'Initialize orchestra on Amazon'):
        #     self.amazon.init_api(SCENARIO_PATH, flush=True)
        # if confirm(u'Start events loop'):
        #     self.events_loop()

    def deploy_maas(self):
        u"""
        Deploy a full OSCIED setup on the EBU's private cluster composed of 4 machines handled by a Canonical's MAAS
        cluster controller.

        TODO

        """
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
        u"""
        Deploy a full OSCIED setup on the public infrastructure (IaaS) of the cloud provider, here Amazon AWS Elastic
        Compute Cloud.

        TODO

        """
        self.amazon.bootstrap(wait_started=True)
        self.amazon.deploy(u'oscied-transform', u'oscied-transform', local=True,
                           constraints=u'arch=amd64 cpu-cores=1 mem=3G')
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

    def register_admins(self):
        u"""Register administrator users required to drive all of the deployed OSCIED setups."""
        self.admins = {}
        for environment in self.environments:
            if environment.name == u'maas': continue  # FIXME remove this at IBC 2013
            print(u'Register or retrieve an administrator in environment {0}.'.format(environment.name))
            admin = User(first_name=u'Mister admin', last_name=u'IBC2013', mail=u'admin.ibc2013@oscied.org',
                        secret='big_secret_to_sav3', admin_platform=True)
            self.admins[environment.name] = environment.api_client.login_or_add(admin)

    def events_loop(self):
        u"""
        Prepare the events-based client "main" loop and periodically calls the event handling method.

        TODO

        """
        #if os.path.exists(u'statistics.json'):
        #    with open(u'statistics.json', u'r', u'utf-8') as f:
        #        self.statistics = json2object(f.read())
        #else:
        #self.environment = u'amazon'
        self.register_admins()

        # Here start the event loop of the demo !
        old_index = None
        while True:
            # Get current time to retrieve state
            now, now_string = datetime_now(format=None), datetime_now()
            index = now.second if ENABLE_TESTING else now.minute
            if index != old_index:
                old_index = index
                self.handle_event(index, now_string)
            else:
                print(u'Skip already consumed event(s) for minute {0}.'.format(index))
            now = datetime_now(format=None)
            sleep_time = 0.8 if ENABLE_TESTING else 60 - now.second
            print(u'Sleep {0} seconds ...'.format(sleep_time))
            time.sleep(sleep_time)
        #try:
        #    with open(u'statistics.json.tmp', u'w', u'utf-8') as f:
        #        f.write(object2json(self.statistics))
        #    os.rename(u'statistics.json.tmp', u'statistics.json')
        #finally:
        #    try_remove(u'statistics.json.tmp')

    def handle_event(self, index, now_string):
        u"""
        Schedule new units and drives the deployed OSCIED setups by using the RESTful API of the orchestration service
        to run encoding and distribution tasks.

        TODO

        """
        for environment in self.environments:
            env_name = environment.name
            # api_client = environment.api_client
            # api_client.auth = self.admins[env_name]
            event = environment.events.get(index, {})
            print(u'Handle {0} scheduled event for minute {1} = {2}.'.format(env_name, index, event))
            for service, stats in environment.statistics.items():
                label, mapper = LABELS[service], MAPPERS[service]
                planned = event.get(service, None)
                stats.units_planned.append(planned)
                # print(len(api_client.transform_profiles.list()))
                # print(len(api_client.transform_profiles.list(spec={'encoder_name': {'$ne': 'copy'}})))
                # print(len(api_client.transform_units))
                # print(len(api_client.publisher_units))
                if env_name == u'maas':                           # FIXME remove this at IBC 2013
                    stats.units_current[STARTED].append(planned)  # FIXME remove this at IBC 2013
                    for state in PENDING_STATES + ERROR_STATES:   # FIXME remove this at IBC 2013
                        stats.units_current[state].append(0)      # FIXME remove this at IBC 2013
                else:                                             # FIXME remove this at IBC 2013
                    api_client = environment.api_client           # FIXME remove this at IBC 2013
                    api_client.auth = self.admins[env_name]       # FIXME remove this at IBC 2013
                    units = getattr(api_client, mapper).list() if ENABLE_UNITS_API else environment.get_units(service)
                    stats.update(now_string, planned, units)
                    delta = planned - len(units)
                    if delta > 0:
                        print(u'Deploy {0} instances'.format(delta))
                    elif delta < 0:
                        delta = -delta
                        print(u'Remove {0} instances'.format(delta))
                    else:
                        print(u'Nothing to do !')
                    #environment.deploy(service,)
                stats.generate_line_chart()
                stats.generate_pie_chart_by_status()

if __name__ == u'__main__':
    configure_unicode()
    IBC2013().main(environments=[
        OsciedEnvironment(u'amazon', config=CONFIG_AMAZ, release=u'raring',  statistics=STATS_AMAZ, events=EVENTS_AMAZ),
        OsciedEnvironment(u'maas',   config=CONFIG_MAAS, release=u'precise', statistics=STATS_MAAS, events=EVENTS_MAAS)
    ])
