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
Statistics helpers of the demo scenario shown during the International Broadcasting Convention at RAI Amsterdam in 2013.

TODO

"""

import os, shutil
import library.pygal as pygal
from library.oscied_lib.pyutils.py_collections import pygal_deque
from library.oscied_lib.pyutils.py_juju import ALL_STATES, ERROR_STATES, PENDING_STATES, STARTED_STATES, STARTED
from library.oscied_lib.pyutils.py_serialization import PickleableObject
from scenario_config import ENABLE_TESTING, LABELS, CHARTS_PATH, TIME_SCALE


class ServiceStatistics(PickleableObject):
    u"""A brand new class to store statistics about a service."""

    def __init__(self, environment=None, service=None, time=None, units_planned=None, units_current=None):
        self.environment, self.service = environment, service
        self.time = time or pygal_deque(maxlen=TIME_SCALE)
        self.units_planned = units_planned or pygal_deque(maxlen=TIME_SCALE)
        self.units_current = units_current or {state: pygal_deque(maxlen=TIME_SCALE) for state in ALL_STATES}

    @property
    def service_label(self):
        return LABELS[self.service]

    def update(self, now_string, planned, units):
        current = {state: 0 for state in ALL_STATES}
        for unit in units.values():
            current[unit['agent-state']] += 1
        print(u'{0} - {1} planned {2} current {3}'.format(self.environment, self.service_label, planned, current))
        import random
        for state, number in current.items():
            self.units_current[state].append(number if (not ENABLE_TESTING or number != 0) else random.randint(1,3))

    def generate_line_chart(self, width=300, height=300, explicit_size=True, show_dots=True, truncate_legend=20):
        tmp_file = os.path.join(CHARTS_PATH, u'line_{0}_{1}.new.svg'.format(self.environment, self.service_label))
        dst_file = os.path.join(CHARTS_PATH, u'line_{0}_{1}.svg'.format(self.environment, self.service_label))
        chart = pygal.Line(width=width, height=height, explicit_size=explicit_size, show_dots=show_dots,
                           truncate_legend=truncate_legend)
        chart.title = u'{0} {1} (# of units)'.format(self.environment, self.service_label)
        chart.add('planned', self.units_planned.list)
        chart.add('current', self.units_current[STARTED].list)
        chart.render_to_file(tmp_file)
        shutil.copy(tmp_file, dst_file)

    def generate_pie_chart_by_status(self, width=300, height=300, explicit_size=True):
        tmp_file = os.path.join(CHARTS_PATH, u'pie_{0}_{1}.new.svg'.format(self.environment, self.service_label))
        dst_file = os.path.join(CHARTS_PATH, u'pie_{0}_{1}.svg'.format(self.environment, self.service_label))
        chart = pygal.Pie(width=width, height=height, explicit_size=explicit_size)
        chart.title = u'{0} {1} by status (# of units)'.format(self.environment, self.service_label)
        for states in (ERROR_STATES, STARTED_STATES, PENDING_STATES):
            units_number = sum((self.units_current.get(state, pygal_deque()).last or 0) for state in states)
            chart.add(u'{0} {1}'.format(units_number, states[0]), units_number)
        chart.render_to_file(tmp_file)
        shutil.copy(tmp_file, dst_file)

STATS_AMAZ, STATS_MAAS = {}, {}
for service in (u'oscied-transform', u'oscied-publisher'):
    STATS_AMAZ[service] = ServiceStatistics(u'amazon', service)
    STATS_MAAS[service] = ServiceStatistics(u'maas',   service)
