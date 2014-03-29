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
Entry-point of the demo scenario at EBU.

TODO

"""

from functools import partial
from pytoolbox.console import confirm
from pytoolbox.encoding import configure_unicode
from pytoolbox.juju import DeploymentScenario, C1_MEDIUM
from library.oscied_lib.models import User

from scenario_config import (
    AMAZON, MAAS, CONFIG, EVENTS, STATS, CHARTS_PATH, SCENARIO_PATH,
    ENABLE_UNITS_API, TRANSFORM_MATRIX, TRANSFORM_MAX_PENDING_TASKS, MAX_OUTPUT_MEDIA_ASSETS
)
from scenario_utils import EBUEnvironment


description = u'Launch EBU demo setup (MaaS Cluster with 3 machines + Amazon)'


class EBU(DeploymentScenario):
    u"""
    The demo scenario's main class at EBU.

    TODO

    """
    def get_parser(self, statistics=False, scaling=False, tasks=False, **kwargs):
        HELP_A = u'The public socket to reach the API.'
        HELP_N = u'The public address to reach the storage service.'
        HELP_I = u'Toggle charts / statistics threads.'
        HELP_S = u'Toggle pre-scheduled scaling threads.'
        HELP_T = u'Toggle automatic tasks and assets threads (for demo purpose).'
        parser = super(EBU, self).get_parser(**kwargs)
        parser.add_argument(u'api_nat_socket',      action=u'store', help=HELP_A)
        parser.add_argument(u'storage_nat_address', action=u'store', help=HELP_N)
        parser.add_argument(u'-i', u'--statistics', action=u'store_true', help=HELP_I, default=statistics)
        parser.add_argument(u'-s', u'--scaling',    action=u'store_true', help=HELP_S, default=scaling)
        parser.add_argument(u'-t', u'--tasks',      action=u'store_true', help=HELP_T, default=tasks)
        return parser

    def run(self):
        print(description)
        if confirm(u'Deploy on MAAS', default=False):
            self.deploy_maas()
        if confirm(u'Deploy on Amazon', default=False):
            self.deploy_amazon()
        if confirm(u'Initialize orchestra on MAAS', default=False):
            self.maas.init_api(SCENARIO_PATH, add_users=False, flush=True, backup_medias_in_remote=False)
        if confirm(u'Start events loop', default=True):
            self.events_loop()

    def deploy_maas(self):
        u"""Deploy a full OSCIED setup in the EBU's private cluster (3 machines) provisioned by the MAAS controller."""
        self.maas.symlink_local_charms()
        self.maas.generate_config_from_template()
        self.maas.bootstrap(wait_started=True, timeout=1200, polling_delay=30, synchronize_tools=True)
        ensure = partial(self.maas.ensure_num_units, local=True)
        ensure(u'oscied-storage',   u'oscied-storage',   to=1, num_units=1, expose=True)
        ensure(u'oscied-storage',   u'oscied-storage',   to=2, num_units=2, expose=True)
        ensure(u'oscied-orchestra', u'oscied-orchestra', to=1, num_units=1, expose=True)
        ensure(u'oscied-publisher', u'oscied-publisher', to=2, num_units=1, expose=True)
        ensure(u'oscied-transform', u'oscied-transform', to=1, num_units=1)
        ensure(u'oscied-transform', u'oscied-transform', to=2, num_units=2)
        ensure(u'oscied-storage',   u'oscied-storage',   to=0, num_units=3, expose=True)
        ensure(u'oscied-transform', u'oscied-transform', to=0, num_units=3, expose=True)

        for peer in (u'orchestra', u'webui', u'transform', u'publisher'):
            self.maas.add_relation(u'oscied-storage', u'oscied-{0}'.format(peer))
        self.maas.add_relation(u'oscied-orchestra:api', u'oscied-webui:api')
        self.maas.add_relation(u'oscied-orchestra:transform', u'oscied-transform:transform')
        self.maas.add_relation(u'oscied-orchestra:publisher', u'oscied-publisher:publisher')

    def deploy_amazon(self):
        u"""Deploy the transform service in the infrastructure (IaaS) of the cloud provider, here Amazon AWS EC2."""

        # gather the local configuration of the orchestration unit to configure the transformation service on Amazon
        orchestra_local_cfg = self.maas.get_unit_local_config(u'oscied-orchestra', 0)
        infos = {
            u'mongo_connection': orchestra_local_cfg[u'mongo_node_connection'],
            u'rabbit_connection': orchestra_local_cfg[u'rabbit_connection'],
            u'storage_address': orchestra_local_cfg[u'storage_address'],
            u'storage_fstype': orchestra_local_cfg[u'storage_fstype'],
            u'storage_mountpoint': orchestra_local_cfg[u'storage_mountpoint'],
            u'api_nat_socket': self.args.api_nat_socket,
            u'storage_nat_address': self.args.storage_nat_address
        }
        self.amazon.symlink_local_charms()
        self.amazon.generate_config_from_template(**infos)
        self.amazon.bootstrap(wait_started=True)
        ensure = partial(self.amazon.ensure_num_units, local=True)
        ensure(u'oscied-transform', u'oscied-transform', num_units=2, constraints=C1_MEDIUM)

    def events_loop(self):
        u"""Prepare the events-based client "main" loop and periodically calls the event handling method."""
        self.maas.enable_units_api = ENABLE_UNITS_API
        self.maas.transform_matrix = TRANSFORM_MATRIX
        self.maas.transform_max_pending_tasks = TRANSFORM_MAX_PENDING_TASKS
        self.maas.max_output_media_assets = MAX_OUTPUT_MEDIA_ASSETS
        self.maas.enable_units_status = False
        self.maas.daemons_auth = self.amazon.daemons_auth = self.maas.api_client.auth  # this is the root account
        # start the statistics thread in both environments
        if self.args.statistics:
            self.maas.statistics_thread.start()
            self.amazon.statistics_thread.start()
        # start the tasks scheduling thread in the environment in which orchestra is deployed
        # amazon transformation units will also receive tasks because the jobs are added to a common transform queue
        if self.args.tasks:
            self.maas.tasks_thread.start()
        # start the units scaling thread in the cloud environment
        if self.args.scaling:
            self.amazon.scaling_thread.start()
        # wait until the threads are killed
        for environment in self.environments:
            [thread.join() for thread in environment.threads]
        print u'Exiting Main Thread'

if __name__ == u'__main__':
    configure_unicode()
    EBU(environments=[
        EBUEnvironment(AMAZON, events=EVENTS[AMAZON], statistics=STATS[AMAZON], charts_path=CHARTS_PATH,
                       config=CONFIG[AMAZON], release=u'raring'),
        EBUEnvironment(MAAS, events=EVENTS[MAAS], statistics=STATS[MAAS], charts_path=CHARTS_PATH,
                       config=CONFIG[MAAS], release=u'precise')
    ]).run()

