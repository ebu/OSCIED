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

from functools import partial
from library.oscied_lib.models import Media, TransformTask
from pytoolbox import juju as py_juju
from pytoolbox.console import confirm
from pytoolbox.juju import DeploymentScenario, C1_MEDIUM
from pytoolbox.subprocess import cmd

from datetime import datetime

try:
    import paya.history
except:
    cmd(u'pip install git+git://github.com/kyouko-taiga/paya.git#egg=paya')
    import paya.history

SCENARIO_PATH = os.path.dirname(__file__)
CONFIG = os.path.join(SCENARIO_PATH, u'config.yaml')

STORAGE_TRANSFORM_UNITS = 2
C1_XLARGE = u'arch=amd64 cpu-cores=8 cpu-power=2000 mem=6G'

def start_monitor(target, args=[], daemon=True):
    t = threading.Thread(target=target, args=args)
    t.daemon = daemon
    t.start()

def monitor_unit_status(environment, history, interval=15):
    while True:
        time_zero = time.time()
        units     = {}
        status    = environment.status(fail=False)
        if status:
            services = status.get(u'services', {})
            for service in services.itervalues():
                units.update({k:v[u'agent-state'] for k,v in service['units'].iteritems()})
            history.append(units)
        time.sleep(max(0, interval - (time.time() - time_zero)))

def monitor_task_status(api, task_ids, history, interval=15):
    _extract_info = lambda task: {u'status': task.status, u'statistic': task.statistic}
    while True:
        time_zero = time.time()
        try:
            history.append({_id: _extract_info(api.transform_tasks[_id]) for _id in task_ids})
            time.sleep(max(0, interval - (time.time() - time_zero)))
        except (ConnectionError, Timeout) as e:
            print(u'WARNING! Communication error while monitoring tasks, details: {1}.'.format(e))

def send_task_set(api, task_set):
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
        time.sleep(0.3)

    # schedule tasks
    return scheduled_tasks

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
        concurrency = kwargs.get('concurrency', 8)
        benchmark   = self.dev

        # initialize environment configuration and bootstrap it
        benchmark.symlink_local_charms()
        benchmark.generate_config_from_template(overwrite=overwrite, concurrency=concurrency)
        benchmark.bootstrap(wait_started=True)

        # deploy juju units
        if confirm(u'Deploy OSCIED units'):
            benchmark.auto   = False
            ensure_num_units = partial(benchmark.ensure_num_units, constraints=C1_XLARGE, local=True)
            ensure_num_units(u'oscied-orchestra', u'oscied-orchestra', expose=True, constraints=C1_MEDIUM)
            ensure_num_units(u'oscied-storage',   u'oscied-storage',   num_units=STORAGE_TRANSFORM_UNITS)

            transform_units = tuple(u'transform-{0}'.format(i) for i in xrange(STORAGE_TRANSFORM_UNITS))
            for i,_ in enumerate(transform_units):
                ensure_num_units(u'oscied-transform', u'oscied-transform', num_units=i+1, to=i+2)

            # setup units relations (except orchestra-transform)
            for peer in (u'oscied-orchestra', u'oscied-transform'):
                benchmark.add_relation(u'oscied-storage', peer)
            # benchmark.add_relation(u'oscied-orchestra:transform', u'oscied-transform:transform')
            benchmark.auto = False

        print(u'start units status monitoring')
        history = paya.history.FileHistory(u'{0}/units-status.paya'.format(SCENARIO_PATH))
        start_monitor(target=monitor_unit_status, args=[benchmark, history])

        # wait for orchestra to be STARTED
        time_start = datetime.now()
        while True:
            print(u'wait for orchestra to start, elapsed: {0}'.format((datetime.now() - time_start)))
            time_zero = time.time()

            units = benchmark.get_units(u'oscied-orchestra')
            state = units['0'].get(u'agent-state', u'unknown')

            if state in py_juju.STARTED_STATES: break
            elif state in py_juju.ERROR_STATES: raise Exception(u'oscied-orchestra failed while starting')
            else:                               time.sleep(max(0, 15 - (time.time() - time_zero)))

        # initialize client API (add users and transform profiles)
        if confirm(u'Initialize OSCIED API'):
            benchmark.init_api(SCENARIO_PATH, flush=True, add_tasks=False, wait_started=True,
                               backup_medias_in_remote=False)

        # setup missing units relations (orchestra-transform)
        # we put the relation between orchestra and transform after we could successfully
        # communicated with orchestra, in order to avoid any misfunction of the unit relation
        benchmark.add_relation(u'oscied-orchestra:transform', u'oscied-transform:transform')

        # TODO: read tasks config file
        config = {
            u'task_sets': [{
                u'input':    u'chsrf.mxf',
                u'output':   u'chsrf.mp4',
                u'profile':  u'Tablet 480p/25',
                u'metadata': {u'title': u'task-mxf-mp4'},
                u'count':    50
            }]
        }

        # get client API object
        api_client = benchmark.api_client
        api_client.login('d@r.com', 'passw0rd')

        if confirm(u'revoke previous tasks'):
            for task in api_client.transform_tasks.list():
                try:
                    del api_client.transform_tasks[task._id]
                except Exception as e:
                    print(repr(e))

        if confirm(u'send task sets to the API'):
            scheduled_tasks = []
            for ts in config['task_sets']:
                scheduled_tasks += send_task_set(api_client, ts)
        else: exit(0)

        print(u'start tasks status monitoring')
        history = paya.history.FileHistory(u'{0}/task-status.paya'.format(SCENARIO_PATH))
        start_monitor(target=monitor_task_status,
                      args=[api_client, [t._id for t in scheduled_tasks], history])

        loop = len(scheduled_tasks) > 0
        while loop:
            print(u'wait for tasks completion')
            states  = {}
            percent = 0.0
            try:
                for st in scheduled_tasks:
                    task = api_client.transform_tasks[st._id]
                    states[task.status] = states.get(task.status, 0) + 1
                    percent += task.statistic.get('percent', 0)

                    undef   = task.status in TransformTask.UNDEF_STATUS
                    running = task.status in TransformTask.RUNNING_STATUS
                    pending = task.status in TransformTask.PENDING_STATUS
                    loop = running or pending or undef

                print(u'\tstates:   ' + u', '.join(['{0}: {1}'.format(k, v) for k,v in states.iteritems()]))
                print(u'\tprogress: ' + str(percent / len(scheduled_tasks)) + '%')
                time.sleep(10)

            except Exception as e:  # except (ConnectionError, Timeout) as e:
                print(u'WARNING! Communication error, details: {1}.'.format(e))

        print(u'retrieve paya histories')
        for unit_type in ['orchestra', 'storage', 'transform']:
            units = benchmark.get_units(u'oscied-{0}'.format(unit_type))
            for unit_no in units:
                try:
                    src = u'oscied-{0}/{1}:/tmp/{0}.paya'.format(unit_type, unit_no)
                    dst = u'{0}/{1}-{2}.paya'.format(SCENARIO_PATH, unit_type, unit_no)
                    cmd(u'juju scp {0} {1}'.format(src, dst))
                    if not os.path.exists(dst):
                        print(u'failed to download {0}'.format(src))
                except Exception as e:
                    print(u'failed to download history from oscied-{0}/{1}'.format(unit_type, unit_no))

        # TODO: benchmark.check_status(raise_if_errors=True, wait_all_started=True)
