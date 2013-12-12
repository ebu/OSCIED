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

from library.oscied_lib.models import TransformTask
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

def monitor_unit_status(environment, history, interval=15):
    while True:
        units    = {}
        services = environment.status[u'services']
        for _,service in services.iteritems():
            units.update({k:v[u'agent-state'] for k,v in service['units'].iteritems()})
        history.append(units)
        time.sleep(interval)

def monitor_task_status(api, task_ids, history, interval=15):
    _extract_info = lambda task: {u'status': task.status, u'statistic': task.statistic}
    while True:
        time_zero = time.time()
        history.append({_id: _extract_info(api.transform_tasks[_id]) for _id in task_ids})
        time.sleep(max(interval - (time.time() - time_zero), 0))

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
        benchmark   = self.dev

        if False:
            # initialize environment configuration and bootstrap it
            benchmark.symlink_local_charms()
            benchmark.generate_config_from_template(overwrite=overwrite, concurrency=concurrency)
            benchmark.bootstrap(wait_started=True)

            # deploy juju units
            if confirm(u'Deploy OSCIED units'):
                benchmark.auto = True
                ensure_num_units = benchmark.ensure_num_units
                #ensure_num_units(u'oscied-storage',   u'oscied-storage',   local=True, num_units=1)
                ensure_num_units(u'oscied-orchestra', u'oscied-orchestra', local=True, expose=True)
                ensure_num_units(u'oscied-storage',   u'oscied-storage',   local=True, num_units=STORAGE_UNITS)
                ensure_num_units(u'oscied-transform', u'oscied-transform', local=True, num_units=TRANSFORM_UNITS)

                # setup units relations
                for peer in (u'orchestra', u'transform'):
                    benchmark.add_relation(u'oscied-storage', u'oscied-{0}'.format(peer))
                benchmark.add_relation(u'oscied-orchestra:transform', u'oscied-transform:transform')
                benchmark.auto = False

            print(u'start monitoring the units status')
            history = paya.history.FileHistory(u'{0}/units-status.paya'.format(SCENARIO_PATH))
            threading.Thread(target=monitor_unit_status, args=[benchmark, history]).start()

        # wait for orchestra to be STARTED
        time_zero = datetime.now()
        while True:
            print(u'wait for orchestra to start, ellapsed: {0}'.format((datetime.now() - time_zero)))
            break

            units = benchmark.get_units(u'oscied-orchestra')
            state = units['0'].get(u'agent-state', u'unknown')

            if state in py_juju.STARTED_STATES: break
            elif state in py_juju.ERROR_STATES: raise Exception(u'oscied-orchestra failed while starting')
            else:                               time.sleep(1)

        # TODO: read tasks config file
        config = {
            u'task_sets': [{
                u'input':    u'Extremes_CHSRF-Lausanne_Mens_200m-50368e4c43ca3.mxf',
                u'output':   u'mxf_to_mp4.mp4',
                u'profile':  u'Tablet 480p/25',
                u'metadata': {u'title': u'mxf_to_mp4'},
                u'count':    0
            }]
        }

        # get client API object
        api_client = benchmark.api_client
        api_client.login('d@f.com', 'oscied3D1')

        print(u'send task sets to the API')
        scheduled_tasks = []
        for ts in config['task_sets']:
            scheduled_tasks += self.send_task_set(api_client, ts)

        print(u'start monitoring the tasks status')
        history = paya.history.FileHistory(u'{0}/task-status.paya'.format(SCENARIO_PATH))
        t = threading.Thread(target=monitor_task_status,
                             args=[api_client, [t._id for t in scheduled_tasks], history])
        t.daemon = True
        t.start()

        print(u'wait for tasks completion')
        while True:
            for st in scheduled_tasks:
                status = api_client.transform_tasks[st._id].status
                if status not in TransformTask.FINAL_STATUS:
                    break
            else: break
            time.sleep(30)

        # TODO: for each unit
        #    cmd(u'juju scp oscied-storage/0:/tmp/history.paya {0}/.'.format(SCENARIO_PATH))
        #    if not os.path.exists(u'history.paya'):
        #        print(u'failed to download paya history')

        # TODO: oscied_lib/api/utils.py:58
        #       wait_started blocks until oscied-orchestra is up and running;
        #       this functionality should be tested
        # benchmark.init_api(SCENARIO_PATH, flush=True, add_tasks=False, wait_started=True)
        # benchmark.check_status(raise_if_errors=True, wait_all_started=True)

    def send_task_set(self, api, task_set):
        # retrieve media and profile objects from api
        media   = api.medias.list(spec={u'filename': task_set[u'input']})[0]
        profile = api.transform_profiles.list(spec={u'title': task_set[u'profile']})[0]
        
        # start transform task
        scheduled_tasks = []
        for i in xrange(task_set['count']):
            scheduled_tasks.append(api.transform_tasks.add({
                u'filename': task_set['output'],
                u'media_in_id': media._id,
                u'profile_id': profile._id,
                u'send_email': False,
                u'queue': u'transform',
                u'metadata': task_set['metadata']
            }))
        
        # schedule tasks
        return scheduled_tasks
