#!/usr/bin/env python
# -*- coding: utf-8 -*-

#**********************************************************************************************************************#
#              OPEN-SOURCE CLOUD INFRASTRUCTURE FOR ENCODING AND DISTRIBUTION : SCENARIOS
#
#  Project Manager : Bram Tullemans (tullemans@ebu.ch)
#  Main Developer  : David Fischer (david.fischer.ch@gmail.com)
#  Co-Developer    : Dimitri Racordon (dimitri.racordon@gmail.com)
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

import time

from pytoolbox import juju as py_juju
from pytoolbox.juju import DeploymentScenario

SCENARIO_PATH = dirname(__file__)
CONFIG = join(SCENARIO_PATH, u'config.yaml')

STORAGE_UNITS = 5
TRANSFORM_UNITS = 5

class Benchmark(DeploymentScenario):

    def run(self, **kwargs):
        u"""
        Run the Benchmark One scenario.

        Keyword arguments:
        concurrency      -- the number of concurrent worker per transformation unit (default 1)
        overwrite_config -- overwrite previously generated configuration file (default False)
        """
        
        overwrite   = kwargs.get('overwrite_config', False)
        concurrency = kwargs.get('concurrency', 1)
        self.benchmark.bootstrap(wait_started=True)
        self.benchmark.generate_config_from_template(overwrite=overwrite, concurrency=concurrency)
        
        self.benchmark.auto = True
        ensure_num_units = self.benchmark.ensure_num_units
        ensure_num_units(u'oscied-orchestra', u'oscied-orchestra', local=True, expose=True)
        ensure_num_units(u'oscied-storage',   u'oscied-storage',   local=True, num_units=STORAGE_UNITS)
        ensure_num_units(u'oscied-transform', u'oscied-transform', local=True, num_units=TRANSFORM_UNITS)

        for peer in (u'orchestra', u'transform')
            self.benchmark.add_relation(u'oscied-storage', u'oscied-{0}'.format(peer))
        self.benchmark.add_relation(u'oscied-orchestra:transform', u'oscied-transform:transform')
        self.benchmark.auto = False

        # wait for orchestra to be STARTED
        while True:
            units = self.bechmark.get_units(u'oscied-orchestra')
            state = units[0].get(u'agent-state', u'unknown')
            if state in py_juju.STARTED_STATES: break
            elif state in py_juju.ERROR_STATES: raise Exception(u'oscied-orchestra failed while starting')
            else:                               time.sleep(0.5)

        # TODO: oscied_lib/api/base.py:119
        #       wait_started blocks until oscied-orchestra is up and running
        #       this functionality should be tested
        self.benchmark.init_api(SCENARIO_PATH, flush=True, add_tasks=False, wait_started=True)

        # TODO self.benchmark.check_status(raise_if_errors=True, wait_all_started=True)
