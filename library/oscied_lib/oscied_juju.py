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

import pygal, random, shutil, threading, time
import pyutils.py_juju as py_juju
from os.path import join, splitext
from collections import defaultdict, deque
from kitchen.text.converters import to_bytes
from requests.exceptions import ConnectionError, Timeout
from oscied_api import OrchestraAPIClient, init_api
from oscied_constants import (ENVIRONMENT_TO_LABEL, ENVIRONMENT_TO_TYPE, SERVICE_TO_LABEL, SERVICE_TO_UNITS_API,
                              SERVICE_TO_TASKS_API)
from oscied_models import Media, OsciedDBTask
from pyutils.py_collections import pygal_deque
from pyutils.py_datetime import datetime_now
from pyutils.py_juju import Environment
from pyutils.py_serialization import PickleableObject


class OsciedEnvironment(Environment):

    # FIXME an helper to update config passwords (generate) -> self.config
    def __init__(self, name, events, statistics, charts_path, api_unit=u'oscied-orchestra/0', enable_units_api=False,
                 enable_units_status=True, enable_tasks_status=True, daemons_auth=None,
                 transform_matrix=None, transform_max_wip_tasks=10, max_output_media_assets=15, **kwargs):
        super(OsciedEnvironment, self).__init__(name, **kwargs)
        self.events = events
        self.statistics = statistics
        self.charts_path = charts_path
        self.api_unit = api_unit
        self.enable_units_api = enable_units_api
        self.enable_units_status = enable_units_status
        self.enable_tasks_status = enable_tasks_status
        self.daemons_auth = daemons_auth
        self.transform_matrix = transform_matrix
        self.transform_max_wip_tasks = transform_max_wip_tasks
        self.max_output_media_assets = max_output_media_assets
        self._api_client = self._statistics_thread = self._scaling_thread = self._tasks_thread = None

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

    @property
    def tasks_thread(self):
        if not self._tasks_thread:
            self._tasks_thread = TasksThread(u'{0} TASKS THREAD'.format(self.name.upper()), self)
        return self._tasks_thread

    def init_api(self, api_init_csv_directory, **kwargs):
        init_api(self.api_client, api_init_csv_directory, **kwargs)

    @property
    def threads(self):
        return filter(None, [self._statistics_thread, self._scaling_thread, self._tasks_thread])


class OsciedEnvironmentThread(threading.Thread):

    def __init__(self, name, environment, daemon=True):
        super(OsciedEnvironmentThread, self).__init__()
        self.name = name
        self.environment = environment
        self.daemon = daemon

    def sleep(self):
        now = datetime_now(format=None)
        sleep_time = self.environment.events.sleep_time(now)
        print(u'[{0}] Sleep {1} seconds ...'.format(self.name, sleep_time))
        time.sleep(sleep_time)


class ServiceStatistics(PickleableObject):
    u"""Store statistics about a service."""

    def __init__(self, environment=None, service=None, time=None, units_planned=None, units_current=None,
                 tasks_current=None, unknown_states=None, maxlen=100):
        self.environment, self.service = environment, service
        self.time = time or deque(maxlen=maxlen)
        self.units_planned = units_planned or pygal_deque(maxlen=maxlen)
        self.units_current = units_current or {state: pygal_deque(maxlen=maxlen) for state in py_juju.ALL_STATES}
        self.tasks_current = tasks_current or {status: deque(maxlen=maxlen) for status in self.tasks_status}
        self.unknown_states = defaultdict(int)

    @property
    def environment_label(self):
        return ENVIRONMENT_TO_LABEL.get(self.environment, self.environment)

    @property
    def environment_type(self):
        return ENVIRONMENT_TO_TYPE.get(self.environment, self.environment)

    @property
    def service_label(self):
        return SERVICE_TO_LABEL.get(self.service, self.service)

    @property
    def tasks_status(self):
        return (OsciedDBTask.PENDING, OsciedDBTask.PROGRESS) # OsciedDBTask.SUCCESS, 

    def update(self, now_string, planned, units, tasks):
        self.units_planned.append(planned)
        current = defaultdict(int)
        for unit in units.values():
            state = unit.get(u'agent-state', u'unknown')
            if state in py_juju.ALL_STATES:
                current[state] += 1
            else:
                self.unknown_states[state] += 1
        for state, history in self.units_current.items():
            history.append(current[state])
        if tasks is not None:
            current = defaultdict(int)
            for task in tasks:
                status = task.status
                if status in OsciedDBTask.PENDING_STATUS:
                    current[OsciedDBTask.PENDING] += 1
                elif status in OsciedDBTask.RUNNING_STATUS:
                    current[OsciedDBTask.PROGRESS] += 1
                elif status in OsciedDBTask.SUCCESS_STATUS:
                    current[OsciedDBTask.SUCCESS] += 1
                # ... else do not add to statistics.
        for status, history in self.tasks_current.items():
            history.append(current[status])
        self.time.append(now_string)


    def _write_chart(self, chart, charts_path, prefix, add_x_labels=True):
        if add_x_labels:
            chart.x_labels = list(self.time)
            chart.x_labels_major_count = 3
            chart.x_label_rotation = 0
            chart.show_minor_x_labels = False
        chart.explicit_size = True
        chart.order_min = 0
        chart.truncate_label = 20
        chart.truncate_legend = 20
        tmp_file = join(charts_path, u'{0}_{1}_{2}.new.svg'.format(prefix, self.environment, self.service_label))
        dst_file = join(charts_path, u'{0}_{1}_{2}.svg'.format(prefix, self.environment, self.service_label))
        chart.render_to_file(tmp_file)
        shutil.copy(tmp_file, dst_file)
        return dst_file

    def generate_units_pie_chart_by_status(self, charts_path, width=300, height=300):
        chart = pygal.Pie(width=width, height=height, no_data_text=u'No unit')
        chart.title = u'Number of {0} {1} nodes'.format(self.environment_type, self.service_label)
        for states in (py_juju.ERROR_STATES, py_juju.STARTED_STATES, py_juju.PENDING_STATES):
            units_number = sum((self.units_current.get(state, pygal_deque()).last or 0) for state in states)
            chart.add(u'{0} {1}'.format(units_number, states[0]), units_number)
        return self._write_chart(chart, charts_path, u'pie_units', add_x_labels=False)

    def generate_units_line_chart(self, charts_path, width=700, height=300):
        chart = pygal.Line(width=width, height=height, show_dots=True, no_data_text=u'No unit')
        chart.title = u'Number of {0} nodes'.format(self.service_label)
        planned_list, current_list = self.units_planned.list, self.units_current[py_juju.STARTED].list
        chart.add(u'{0} planned'.format(planned_list[-1] if len(planned_list) > 0 else 0), planned_list)
        chart.add(u'{0} current'.format(current_list[-1] if len(current_list) > 0 else 0), current_list)
        return self._write_chart(chart, charts_path, u'line_units')

    def generate_tasks_line_chart(self, charts_path, width=1200, height=300):
        total, lines = 0, {}
        for status in self.tasks_status:
            current_list = list(self.tasks_current[status])
            number = current_list[-1] if len(current_list) > 0 else 0
            total += number
            lines[status] = (number, current_list)
        # , range=(0, total)
        chart = pygal.StackedLine(fill=True, width=width, height=height, show_dots=False, no_data_text=u'No task')
        chart.title = u'Scheduling of {0} tasks on {1}'.format(self.service_label, self.environment_label)

        for status in self.tasks_status:
            chart.add(u'{0} {1}'.format(lines[status][0], status), lines[status][1])
        return self._write_chart(chart, charts_path, u'line_tasks')


class ScalingThread(OsciedEnvironmentThread):
    u"""Handle the scaling of a deployed OSCIED setup."""

    def run(self):
        while True:
            # Get current time to retrieve state
            env, now, now_string = self.environment, datetime_now(format=None), datetime_now()
            try:
                env.auto = True  # Really better like that ;-)
                index, event = env.events.get(now, default_value={})
                print(u'[{0}] Handle scaling at index {1}.'.format(self.name, index))
                for service, stats in env.statistics.items():
                    label = SERVICE_TO_LABEL.get(service, service)
                    units_api = SERVICE_TO_UNITS_API[service]
                    planned = event.get(service, None)
                    if env.enable_units_api:
                        api_client = env.api_client
                        api_client.auth = env.daemons_auth
                        units = getattr(api_client, units_api).list()
                    else:
                        units = env.get_units(service)
                    if len(units) != planned:
                        print(u'[{0}] Ensure {1} instances of service {2}'.format(self.name, planned, label))
                        env.ensure_num_units(service, service, num_units=planned)
                        env.cleanup_machines()  # Safer way to terminate machines !
                    else:
                        print(u'[{0}] Nothing to do !'.format(self.name))
            except (ConnectionError, Timeout) as e:
                # FIXME do something here ...
                print(u'[{0}] WARNING! Communication error, details: {1}.'.format(self.name, e))
            self.sleep()


class StatisticsThread(OsciedEnvironmentThread):
    u"""Update statistics and generate charts of the deployed OSCIED setups."""

    def run(self):
        while True:
            # Get current time to retrieve state
            env, now, now_string = self.environment, datetime_now(format=None), datetime_now()
            try:
                env.auto = True  # Really better like that ;-)
                index, event = env.events.get(now, default_value={})
                print(u'[{0}] Update charts at index {1}.'.format(self.name, index))
                for service, stats in env.statistics.items():
                    label = SERVICE_TO_LABEL.get(service, service)
                    units_api, tasks_api = SERVICE_TO_UNITS_API[service], SERVICE_TO_TASKS_API[service]
                    planned = event.get(service, None)
                    api_client = env.api_client
                    api_client.auth = env.daemons_auth
                    if env.enable_units_status:
                        if env.enable_units_api:
                            units = getattr(api_client, units_api).list()
                        else:
                            units = env.get_units(service)
                    else:
                        units = {k: {u'agent-state': py_juju.STARTED} for k in range(planned)}
                    tasks = getattr(api_client, tasks_api).list(head=True) if env.enable_tasks_status else None
                    stats.update(now_string, planned, units, tasks)
                    stats.generate_units_pie_chart_by_status(env.charts_path)
                    stats.generate_units_line_chart(env.charts_path)
                    stats.generate_tasks_line_chart(env.charts_path)
                    stats.write()
            except (ConnectionError, Timeout) as e:
                # FIXME do something here ...
                print(u'[{0}] WARNING! Communication error, details: {1}.'.format(self.name, e))
            self.sleep()


class TasksThread(OsciedEnvironmentThread):
    u"""Drives a deployed OSCIED setup to transcode, publish and cleanup media assets."""

    @staticmethod
    def get_media_or_raise(medias, media_title):
        u"""Return a media asset with title ``media_title`` or raise an IndexError."""
        try:
            return next(media for media in medias if media.metadata['title'] == media_title)
        except StopIteration:
            raise IndexError(to_bytes(u'Missing media asset "{0}".'.format(media_title)))

    @staticmethod
    def get_profile_or_raise(profiles, profile_title):
        u"""Return a transformation profile with title ``profile_title`` or raise an IndexError."""
        try:
            return next(profile for profile in profiles if profile.title == profile_title)
        except StopIteration:
            raise IndexError(to_bytes(u'Missing transformation profile "{0}".'.format(profile_title)))

    @staticmethod
    def launch_transform(api_client, media_in, profile, title_prefix, filename_suffix):
        in_title = media_in.metadata['title']
        out_title = u'{0} {1}'.format(title_prefix, in_title)
        metadata = {u'title': out_title, u'profile': profile.title}
        print(u'Transcode "{0}" to "{1}" with profile {2} ...'.format(in_title, out_title, profile.title))
        return api_client.transform_tasks.add({
            u'filename': profile.output_filename(media_in.filename, suffix=filename_suffix),
            u'media_in_id': media_in._id, u'profile_id': profile._id, u'send_email': False,
            u'queue': u'transform_private', u'metadata': metadata
        })

    @staticmethod
    def transform(api_client, medias, profiles, matrix, maximum, output_counter):
        u"""Transcode source media assets with chosen profiles limiting amount of running tasks."""
        wip = OsciedDBTask.WORK_IN_PROGRESS_STATUS
        output_count = sum(1 for t in api_client.transform_tasks.list(head=True) if t.status in wip)
        counter = maximum - output_count
        # FIXME I do not why but $in operator does not work !
        # api_client.transform_tasks.count(spec={'status': {'$in': OsciedDBTask.WORK_IN_PROGRESS_STATUS}})
        if counter <= 0:
            print(u'No need to create any media asset, already processing {0} of them.'.format(output_count))
        else:
            s = u's' if counter > 1 else u''
            print(u'Launch {0} transcoding task{1} to create media assets.'.format(counter, s))
            for i in range(counter):
                media_title, profile_title = random.choice(matrix)
                media = TasksThread.get_media_or_raise(medias, media_title)
                profile = TasksThread.get_profile_or_raise(profiles, profile_title)
                TasksThread.launch_transform(api_client, media, profile,
                                             u'Output {0}'.format(output_counter),
                                             u'_output_{0}'.format(output_counter))
                output_counter += 1
        return output_counter

    @staticmethod
    def cleanup_media_assets(api_client, maximum):
        u"""Ensure ``maximum`` output media assets in shared storage by deleting the oldest."""
        medias = api_client.medias.list(head=True, sort=[(u'metadata.add_date', 1)])
        output_medias = [m for m in medias if m.status == Media.READY and m.parent_id]
        counter = len(output_medias) - maximum
        if counter <= 0:
            print(u'No need to delete any output media asset, they are {0} ready and limit is {1}.'.format(
                  len(output_medias), maximum))
        else:
            s = u's' if counter > 1 else u''
            print(u'Delete {0} output media asset{1} to keep at most {2} of them.'.format(counter, s, maximum))
            for i in range(counter):
                media = output_medias.pop()
                print(u'Delete output media asset "{0}".'.format(media.metadata['title']))
                assert(media.parent_id)
                del api_client.medias[media._id]

    def run(self):
        output_counter = 0
        while True:
            # Get current time to retrieve state
            env, now, now_string = self.environment, datetime_now(format=None), datetime_now()
            try:
                env.auto = True  # Really better like that ;-)
                api_client = env.api_client
                api_client.auth = env.daemons_auth

                # Get all media assets and detect source media assets (not resulting of a transformation task)
                medias = api_client.medias.list(head=True, spec={'status': {'$ne': Media.DELETED}})
                profiles = api_client.transform_profiles.list()

                output_counter = TasksThread.transform(api_client, medias, profiles, env.transform_matrix,
                                                       env.transform_max_wip_tasks, output_counter)

                TasksThread.cleanup_media_assets(api_client, env.max_output_media_assets)

            except (ConnectionError, Timeout) as e:
                # FIXME do something here ...
                print(u'[{0}] WARNING! Communication error, details: {1}.'.format(self.name, e))
            self.sleep()
