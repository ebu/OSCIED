#!/usr/bin/env python
# -*- coding: utf-8 -*-

#**********************************************************************************************************************#
#              OPEN-SOURCE CLOUD INFRASTRUCTURE FOR ENCODING AND DISTRIBUTION : SCENARIOS
#
#  Project Manager : Bram Tullemans (tullemans@ebu.ch)
#  Main Developer  : Dimitri Racordon (dimitri.racordon@gmail.com)
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

import os, threading, time

from pytoolbox import juju as py_juju
from pytoolbox.console import confirm
from pytoolbox.juju import DeploymentScenario
from pytoolbox.subprocess import cmd

from datetime import datetime

try:
    import paya.history
except:
    cmd(u'pip install git+git://github.com/kyouko-taiga/paya.git#egg=paya')
    import paya.history

SCENARIO_PATH = os.path.dirname(__file__)
CONFIG = os.path.join(SCENARIO_PATH, u'config.yaml')

STORAGE_UNITS = 1
TRANSFORM_UNITS = 5

def monitor_unit_status(environment, history, interval=5):
    while True:
        units    = {}
        services = environment.status[u'services']
        for _,service in services.iteritems():
            units.update({k:v[u'agent-state'] for k,v in service['units'].iteritems()})
        history.append(units)

        time.sleep(interval)

class Benchmark(DeploymentScenario):

    def run(self, **kwargs):
        u"""
        Run the Benchmark One scenario.

        Keyword arguments:
        concurrency      -- the number of concurrent worker per transformation unit (default 1)
        overwrite_config -- overwrite previously generated configuration file (default False)
        """

        # get configuration parameters
        overwrite   = kwargs.get('overwrite_config', False)
        concurrency = kwargs.get('concurrency', 1)

        # initialize environment configuration and bootstrap it
        self.benchmark.symlink_local_charms()
        self.benchmark.generate_config_from_template(overwrite=overwrite, concurrency=concurrency)
        self.benchmark.bootstrap(wait_started=True)

        # deploy juju units
        if confirm(u'Deploy OSCIED units'):
            self.benchmark.auto = True
            ensure_num_units = self.benchmark.ensure_num_units
            #ensure_num_units(u'oscied-storage',   u'oscied-storage',   local=True, num_units=1)
            ensure_num_units(u'oscied-orchestra', u'oscied-orchestra', local=True, expose=True)
            ensure_num_units(u'oscied-storage',   u'oscied-storage',   local=True, num_units=STORAGE_UNITS)
            ensure_num_units(u'oscied-transform', u'oscied-transform', local=True, num_units=TRANSFORM_UNITS)

            # setup units relations
            for peer in (u'orchestra', u'transform'):
                self.benchmark.add_relation(u'oscied-storage', u'oscied-{0}'.format(peer))
            self.benchmark.add_relation(u'oscied-orchestra:transform', u'oscied-transform:transform')
            self.benchmark.auto = False

        print(u'start monitoring the units status')
        history = paya.history.FileHistory(u'{0}/units-status.paya'.format(SCENARIO_PATH))
        threading.Thread(target=monitor_unit_status, args=[self.benchmark, history]).start()

        # wait for orchestra to be STARTED
        time_zero = datetime.now()
        while True:
            units = self.benchmark.get_units(u'oscied-orchestra')
            state = units['0'].get(u'agent-state', u'unknown')
            print(u'wait for orchestra to start, ellapsed: {0}'.format((datetime.now() - time_zero)))

            if state in py_juju.STARTED_STATES: break
            elif state in py_juju.ERROR_STATES: raise Exception(u'oscied-orchestra failed while starting')
            else:                               time.sleep(1)
        
        # while True:
        #     units = self.benchmark.get_units(u'oscied-storage')
        #     state = units['0'].get(u'agent-state', u'unknown')
        #     print(u'waiting {0} to be started: current status: {1}'.format(u'oscied-storage', state))
        #     if state in py_juju.STARTED_STATES: break
        #     elif state in py_juju.ERROR_STATES: raise Exception(u'oscied-storage failed while starting')
        #     else:                               time.sleep(0.5)

        time.sleep(30)

        # TODO: for each unit
        #    cmd(u'juju scp oscied-storage/0:/tmp/history.paya {0}/.'.format(SCENARIO_PATH))
        #    if not os.path.exists(u'history.paya'):
        #        print(u'failed to download paya history')

        # TODO: oscied_lib/api/utils.py:58
        #       wait_started blocks until oscied-orchestra is up and running;
        #       this functionality should be tested
        # self.benchmark.init_api(SCENARIO_PATH, flush=True, add_tasks=False, wait_started=True)

        # TODO self.benchmark.check_status(raise_if_errors=True, wait_all_started=True)

    def send_tasks(self):
        api_client = self.benchmark.api_client()

        # retrieves medias list
        medias = api_client.medias.list(head=True)

        # read tasks configuration file
        
        # schedule tasks
        return []