# -*- coding: utf-8 -*-

#**********************************************************************************************************************#
#              OPEN-SOURCE CLOUD INFRASTRUCTURE FOR ENCODING AND DISTRIBUTION : COMMON LIBRARY
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

import os, pygal, shutil, threading, time
from collections import defaultdict
from requests.exceptions import Timeout
from oscied_api import OrchestraAPIClient, init_api, SERVICE_TO_LABEL, SERVICE_TO_MAPPER
from pyutils.py_collections import pygal_deque
from pyutils.py_datetime import datetime_now
from pyutils.py_juju import (
    Environment, ALL_STATES, ERROR_STATES, PENDING_STATES, STARTED_STATES, STOPPED_STATES, STARTED
)
from pyutils.py_serialization import PickleableObject


class OsciedEnvironment(Environment):

    # FIXME an helper to update config passwords (generate) -> self.config
    def __init__(self, name, events, statistics, charts_path, api_unit=u'oscied-orchestra/0', enable_units_api=False,
                 enable_units_status=True, daemons_auth=None, **kwargs):
        super(OsciedEnvironment, self).__init__(name, **kwargs)
        self.events = events
        self.statistics = statistics
        self.charts_path = charts_path
        self.api_unit = api_unit
        self.enable_units_api = enable_units_api
        self.enable_units_status = enable_units_status
        self.daemons_auth = daemons_auth
        self._api_client = self._statistics_thread = self._scaling_thread = None

    @property
    def api_client(self):
        if not self._api_client:
            service, number = self.api_unit.split('/')
            settings = self.get_service_config(service)['settings']
            root_auth = (u'root', settings['root_secret']['value'])
            host = self.get_unit(service, number)['public-address']
            self._api_client = OrchestraAPIClient(host, api_unit=self.api_unit, auth=root_auth, environment=self.name)
        return self._api_client

    @property
    def scaling_thread(self):
        if not self._scaling_thread:
            self._scaling_thread = ScalingThread(u'{0} SCALING THREAD'.format(self.name.upper()), self)
        return self._scaling_thread

    @property
    def statistics_thread(self):
        if not self._statistics_thread:
            self._statistics_thread = StatisticsThread(u'{0} STATISTICS THREAD'.format(self.name.upper()), self)
        return self._statistics_thread

    def init_api(self, api_init_csv_directory, flush=False, **kwargs):
        init_api(self.api_client, api_init_csv_directory, flush=flush)


class ServiceStatistics(PickleableObject):
    u"""Store statistics about a service."""

    def __init__(self, environment=None, service=None, time=None, units_planned=None, units_current=None,
                 unknown_states=None, maxlen=100):
        self.environment, self.service = environment, service
        self.time = time or pygal_deque(maxlen=maxlen)
        self.units_planned = units_planned or pygal_deque(maxlen=maxlen)
        self.units_current = units_current or {state: pygal_deque(maxlen=maxlen) for state in ALL_STATES}
        self.unknown_states = defaultdict(int)

    @property
    def service_label(self):
        return SERVICE_TO_LABEL.get(self.service, self.service)

    def update(self, now_string, planned, units):
        self.units_planned.append(planned)
        current = defaultdict(int)
        for unit in units.values():
            state = unit.get(u'agent-state', u'unknown')
            if state in ALL_STATES:
                current[state] += 1
            else:
                self.unknown_states[state] += 1
        for state, history in self.units_current.items():
            history.append(current[state])

    def generate_line_chart(self, charts_path, width=300, height=300, explicit_size=True, show_dots=True,
                            truncate_legend=20):
        tmp_file = os.path.join(charts_path, u'line_{0}_{1}.new.svg'.format(self.environment, self.service_label))
        dst_file = os.path.join(charts_path, u'line_{0}_{1}.svg'.format(self.environment, self.service_label))
        chart = pygal.Line(width=width, height=height, explicit_size=explicit_size, show_dots=show_dots,
                           truncate_legend=truncate_legend)
        chart.title = u'{0} {1} (# of units)'.format(self.environment, self.service_label)
        chart.add('planned', self.units_planned.list)
        chart.add('current', self.units_current[STARTED].list)
        chart.render_to_file(tmp_file)
        shutil.copy(tmp_file, dst_file)
        return dst_file

    def generate_pie_chart_by_status(self, charts_path, width=300, height=300, explicit_size=True):
        tmp_file = os.path.join(charts_path, u'pie_{0}_{1}.new.svg'.format(self.environment, self.service_label))
        dst_file = os.path.join(charts_path, u'pie_{0}_{1}.svg'.format(self.environment, self.service_label))
        chart = pygal.Pie(width=width, height=height, explicit_size=explicit_size)
        chart.title = u'{0} {1} by status (# of units)'.format(self.environment, self.service_label)
        for states in (ERROR_STATES, STARTED_STATES, PENDING_STATES):
            units_number = sum((self.units_current.get(state, pygal_deque()).last or 0) for state in states)
            chart.add(u'{0} {1}'.format(units_number, states[0]), units_number)
        chart.render_to_file(tmp_file)
        shutil.copy(tmp_file, dst_file)
        return dst_file


class ScalingThread(threading.Thread):
    u"""Handle the scaling of a deployed OSCIED setup."""

    def __init__(self, name, environment, daemon=True):
        super(ScalingThread, self).__init__()
        self.name = name
        self.environment = environment
        self.daemon = daemon

    def run(self):
        while True:
            # Get current time to retrieve state
            now, now_string = datetime_now(format=None), datetime_now()
            try:
                self.environment.auto = True  # Really better like that ;-)
                index, event = self.environment.events.get(now, default_value={})
                print(u'[{0}] Handle scaling at index {1}.'.format(self.name, index))
                for service, stats in self.environment.statistics.items():
                    label, mapper = SERVICE_TO_LABEL.get(service, service), SERVICE_TO_MAPPER[service]
                    planned = event.get(service, None)
                    if self.environment.enable_units_api:
                        api_client = self.environment.api_client
                        api_client.auth = self.environment.daemons_auth
                        units = getattr(api_client, mapper).list()
                    else:
                        units = self.environment.get_units(service)
                    if len(units) != planned:
                        print(u'[{0}] Ensure {1} instances of service {2}'.format(self.name, planned, label))
                        self.environment.ensure_num_units(service, service, num_units=planned)
                        self.environment.cleanup_machines()  # Safer way to terminate machines !
                    else:
                        print(u'[{0}] Nothing to do !'.format(self.name))
            except Timeout as e:
                # FIXME do something here ...
                print(u'[{0}] WARNING! Timeout, reason: {1}.'.format(self.name, e))
            now = datetime_now(format=None)
            sleep_time = self.environment.events.sleep_time(now)
            print(u'[{0}] Sleep {1} seconds ...'.format(self.name, sleep_time))
            time.sleep(sleep_time)


class StatisticsThread(threading.Thread):
    u"""Update statistics and generate charts of the deployed OSCIED setups."""

    def __init__(self, name, environment, daemon=True):
        super(StatisticsThread, self).__init__()
        self.name = name
        self.environment = environment
        self.daemon = daemon

    def run(self):
        while True:
            # Get current time to retrieve state
            now, now_string = datetime_now(format=None), datetime_now()
            try:
                self.environment.auto = True  # Really better like that ;-)
                index, event = self.environment.events.get(now, default_value={})
                print(u'[{0}] Update charts at index {1}.'.format(self.name, index))
                for service, stats in self.environment.statistics.items():
                    label, mapper = SERVICE_TO_LABEL.get(service, service), SERVICE_TO_MAPPER[service]
                    planned = event.get(service, None)
                    if self.environment.enable_units_status:
                        if self.environment.enable_units_api:
                            api_client = self.environment.api_client
                            api_client.auth = self.environment.daemons_auth
                            units = getattr(api_client, mapper).list()
                        else:
                            units = self.environment.get_units(service)
                    else:
                        units = {k: {u'agent-state': STARTED} for k in range(planned)}
                    stats.update(now_string, planned, units)
                    stats.generate_line_chart(self.environment.charts_path)
                    stats.generate_pie_chart_by_status(self.environment.charts_path)
                    stats.write()
            except Timeout as e:
                # FIXME do something here ...
                print(u'[{0}] WARNING! Timeout, reason: {1}.'.format(self.name, e))
            now = datetime_now(format=None)
            sleep_time = self.environment.events.sleep_time(now)
            print(u'[{0}] Sleep {1} seconds ...'.format(self.name, sleep_time))
            time.sleep(sleep_time)
