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
# http://pygal.org/custom_styles/

from library.oscied_lib.oscied_models import User
from library.oscied_lib.oscied_juju import OsciedEnvironment
from library.oscied_lib.pyutils.py_console import confirm
from library.oscied_lib.pyutils.py_juju import DeploymentScenario, M1_SMALL, C1_MEDIUM
from library.oscied_lib.pyutils.py_unicode import configure_unicode

from scenario_config import (CONFIG_AMAZ, EVENTS_AMAZ, STATS_AMAZ,
                             CONFIG_MAAS, EVENTS_MAAS, STATS_MAAS, CHARTS_PATH, SCENARIO_PATH, ENABLE_UNITS_API)


description = u'Launch IBC 2013 demo setup (MaaS Cluster with 4 machines // Amazon)'


class IBC2013(DeploymentScenario):
    u"""
    The demo scenario's main class shown during the International Broadcasting Convention at RAI Amsterdam in 2013.

    TODO

    """

    def get_parser(self, statistics=False, scaling=False, tasks=False, **kwargs):
        HELP_I = u'Toggle charts / statistics threads.'
        HELP_S = u'Toggle pre-scheduled scaling threads.'
        HELP_T = u'Toggle automatic tasks and assets threads (for demo purpose).'
        parser = super(IBC2013, self).get_parser(**kwargs)
        parser.add_argument(u'-i', u'--statistics', action=u'store_true', help=HELP_I, default=statistics)
        parser.add_argument(u'-s', u'--scaling',    action=u'store_true', help=HELP_S, default=scaling)
        parser.add_argument(u'-t', u'--tasks',      action=u'store_true', help=HELP_T, default=tasks)
        return parser

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
        if confirm(u'Start events loop', default=True):
            self.events_loop()

    def deploy_maas(self):
        u"""Deploy a full OSCIED setup in the EBU's private cluster (4 machines) provisioned by the MAAS controller."""
        self.maas.bootstrap(wait_started=True, timeout=1200, polling_delay=30)
        ensure_num_units = self.maas.ensure_num_units
        ensure_num_units(u'oscied-storage',   u'oscied-storage',   local=True, num_units=4, expose=True) # 1,2,3
        # WAIT
        ensure_num_units(u'oscied-orchestra', u'oscied-orchestra', local=True, to=1, expose=True)
        # WAIT
        ensure_num_units(u'oscied-webui',     u'oscied-webui',     local=True, to=1, expose=True)
        ensure_num_units(u'oscied-publisher', u'oscied-publisher', local=True, to=2, expose=True)
        ensure_num_units(u'oscied-publisher', u'oscied-publisher', local=True, to=3, expose=True) #3=5
        # WAIT
        ensure_num_units(u'oscied-transform', u'oscied-transform', local=True, to=1)
        ensure_num_units(u'oscied-transform', u'oscied-transform', local=True, to=2)
        ensure_num_units(u'oscied-transform', u'oscied-transform', local=True, to=3) #3=5
        # WAIT -> Makes juju crazy (/var/log/juju/all-machines.log -> growing to GB)
        ensure_num_units(u'oscied-storage',   u'oscied-storage',   local=True, to=0, expose=True)
        # WAIT -> Makes juju crazy (/var/log/juju/all-machines.log -> growing to GB)
        ensure_num_units(u'oscied-transform', u'oscied-transform', local=True, to=0, expose=True)

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
        u"""Deploy a full OSCIED setup in the infrastructure (IaaS) of the cloud provider, here Amazon AWS EC2."""
        self.amazon.bootstrap(wait_started=True)
        ensure_num_units = self.amazon.ensure_num_units
        ensure_num_units(u'oscied-transform', u'oscied-transform', local=True, constraints=C1_MEDIUM)
        ensure_num_units(u'oscied-publisher', u'oscied-publisher', local=True, constraints=M1_SMALL, expose=True)
        ensure_num_units(u'oscied-orchestra', u'oscied-orchestra', local=True, constraints=M1_SMALL, expose=True)
        # WAIT
        ensure_num_units(u'oscied-storage',   u'oscied-storage', local=True, to=3)
        ensure_num_units(u'oscied-webui',     u'oscied-webui',   local=True, to=3, expose=True)
        for peer in (u'orchestra', u'webui', u'transform', u'publisher'):
            self.amazon.add_relation(u'oscied-storage', u'oscied-{0}'.format(peer))
        self.amazon.add_relation(u'oscied-orchestra:transform', u'oscied-transform:transform')
        self.amazon.add_relation(u'oscied-orchestra:publisher', u'oscied-publisher:publisher')
        self.amazon.add_relation(u'oscied-orchestra:api',       u'oscied-webui:api')

    def events_loop(self):
        u"""Prepare the events-based client "main" loop and periodically calls the event handling method."""
        for environment in self.environments:
            environment.enable_units_api = ENABLE_UNITS_API
            if environment.name == u'maas':
                environment.enable_units_status = False  # FIXME enable it during IBC (??)
                environment.enable_tasks_status = False  # FIXME enable it during IBC
            else:
                print(u'Register or retrieve an administrator in environment {0}.'.format(environment.name))
                admin = User(first_name=u'Mister admin', last_name=u'IBC2013', mail=u'admin.ibc2013@oscied.org',
                            secret='big_secret_to_sav3', admin_platform=True)
                environment.daemons_auth = environment.api_client.login_or_add(admin)
            if self.statistics:
                environment.statistics_thread.start()
            if isinstance(environment.daemons_auth, User):
                if self.scaling:
                    environment.scaling_thread.start()
                if self.tasks:
                    environment.tasks_thread.start()
        for environment in self.environments:
            [thread.join() for thread in environment.threads]
        print u'Exiting Main Thread'

if __name__ == u'__main__':
    configure_unicode()
    IBC2013().main(environments=[
        OsciedEnvironment(u'amazon', EVENTS_AMAZ, STATS_AMAZ, CHARTS_PATH, config=CONFIG_AMAZ, release=u'raring'),
        OsciedEnvironment(u'maas',   EVENTS_MAAS, STATS_MAAS, CHARTS_PATH, config=CONFIG_MAAS, release=u'precise')
    ])
