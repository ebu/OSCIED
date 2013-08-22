# -*- coding: utf-8 -*-

#**********************************************************************************************************************#
#              OPEN-SOURCE CLOUD INFRASTRUCTURE FOR ENCODING AND DISTRIBUTION : COMMON LIBRARY
#
#  Authors   : David Fischer
#  Contact   : david.fischer.ch@gmail.com
#  Project   : OSCIED (OS Cloud Infrastructure for Encoding and Distribution)
#  Copyright : 2012-2013 OSCIED Team. All rights reserved.
#**********************************************************************************************************************#
#
# This file is part of EBU/UER OSCIED Project.
#
# This project is free software: you can redistribute it and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This project is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this project.
# If not, see <http://www.gnu.org/licenses/>
#
# Retrieved from https://github.com/ebu/OSCIED

import os, shutil, time
from celery import current_task, states
from celery.decorators import task
from kitchen.text.converters import to_bytes
from oscied_config import PublisherLocalConfig
from oscied_models import Media
from oscied_util import Callback
from pyutils.py_datetime import datetime_now
from pyutils.py_filesystem import recursive_copy
from pyutils.py_serialization import object2json
from pyutils.py_unicode import configure_unicode
from pyutils.py_validation import valid_uri

configure_unicode()

@task(name=u'PublisherWorker.publish_task')
def publish_task(media_json, callback_json):

    def copy_callback(start_date, elapsed_time, eta_time, src_size, dst_size, ratio):
        publish_task.update_state(state=u'PROGRESS', meta={
            u'hostname': request.hostname, u'start_date': start_date, u'elapsed_time': elapsed_time,
            u'eta_time': eta_time, u'media_size': src_size, u'publish_size': dst_size, u'percent': int(100 * ratio)})

    def publish_callback(status, publish_uri):
        data = {u'task_id': request.id, u'status': status}
        if publish_uri:
            data[u'publish_uri'] = publish_uri
        data_json = object2json(data, False)
        if callback is None:
            print(u'{0} [ERROR] Unable to callback orchestrator: {1}'.format(request.id, data_json))
        else:
            r = callback.post(data_json)
            print(u'{0} Code {1} {2} : {3}'.format(request.id, r.status_code, r.reason, r._content))

    # ------------------------------------------------------------------------------------------------------------------

    RATIO_DELTA = 0.01  # Update status if at least 1% of progress
    TIME_DELTA = 1      # Update status if at least 1 second(s) elapsed

    # Avoid 'referenced before assignment'
    callback = publish_root = None
    request = current_task.request

    try:
        # Let's the task begin !
        print(u'{0} Publication task started'.format(request.id))

        # Read current configuration to translate files uri to local paths
        config = PublisherLocalConfig.read(u'local_config.pkl')
        print(object2json(config, True))

        # Load and check task parameters
        callback = Callback.from_json(callback_json)
        callback.is_valid(True)

        # Update callback socket according to configuration
        if config.api_nat_socket and len(config.api_nat_socket) > 0:
            callback.replace_netloc(config.api_nat_socket)

        media = Media.from_json(media_json)
        media.is_valid(True)

        # Verify that media file can be accessed
        media_path = config.storage_medias_path(media, generate=False)
        if not media_path:
            raise NotImplementedError(to_bytes(u'Media will not be readed from shared storage : {0}'.format(media.uri)))
        publish_path, publish_uri = config.publish_point(media)
        media_root, publish_root = os.path.dirname(media_path), os.path.dirname(publish_path)

        infos = recursive_copy(media_root, publish_root, copy_callback, RATIO_DELTA, TIME_DELTA)
        if not valid_uri(publish_uri, check_404=True):
            raise IOError(to_bytes(u'Media seem unreachable from publication URI {0}'.format(publish_uri)))

        # Here all seem okay
        print(u'{0} Publication task successful, media published as {1}'.format(request.id, publish_uri))
        publish_callback(states.SUCCESS, publish_uri)
        return {u'hostname': request.hostname, u'start_date': infos[u'start_date'],
                u'elapsed_time': infos[u'elapsed_time'], u'eta_time': 0, u'media_size': infos[u'src_size'],
                u'publish_size': infos[u'src_size'], u'percent': 100}

    except Exception as error:

        # Here something went wrong
        print(u'{0} Publication task failed'.format(request.id))
        if publish_root:
            shutil.rmtree(publish_root, ignore_errors=True)
        publish_callback(unicode(error), None)
        raise

@task(name=u'PublisherWorker.revoke_publish_task')
def revoke_publish_task(publish_uri, callback_json):

    def revoke_publish_callback(status, publish_uri):
        data = {u'task_id': request.id, u'status': status}
        if publish_uri:
            data[u'publish_uri'] = publish_uri
        data_json = object2json(data, False)
        if callback is None:
            print(u'{0} [ERROR] Unable to callback orchestrator: {1}'.format(request.id, data_json))
        else:
            r = callback.post(data_json)
            print(u'{0} Code {1} {2} : {3}'.format(request.id, r.status_code, r.reason, r._content))

    # ------------------------------------------------------------------------------------------------------------------

    # Avoid 'referenced before assignment'
    callback = None
    request = current_task.request

    try:
        # Let's the task begin !
        print(u'{0} Revoke publication task started'.format(request.id))

        # Read current configuration to translate files uri to local paths
        config = PublisherLocalConfig.read(u'local_config.pkl')
        print(object2json(config, True))

        # Load and check task parameters
        callback = Callback.from_json(callback_json)
        callback.is_valid(True)

        # Update callback socket according to configuration
        if config.api_nat_socket and len(config.api_nat_socket) > 0:
            callback.replace_netloc(config.api_nat_socket)

        publish_root = os.path.dirname(config.publish_uri_to_path(publish_uri))
        if not publish_root:
            raise ValueError(to_bytes(u'Media is not hosted on this publication point.'))

        # Remove publication directory
        start_date, start_time = datetime_now(), time.time()
        shutil.rmtree(publish_root, ignore_errors=True)
        if valid_uri(publish_uri, check_404=True):
            raise IOError(to_bytes(u'Media seem reachable from publication URI {0}'.format(publish_uri)))
        elapsed_time = time.time() - start_time

        # Here all seem okay
        print(u'{0} Revoke publication task successful, media unpublished from {1}'.format(request.id, publish_uri))
        revoke_publish_callback(states.SUCCESS, publish_uri)
        return {u'hostname': request.hostname, u'start_date': start_date, u'elapsed_time': elapsed_time, u'eta_time': 0,
                u'percent': 100}

    except Exception as error:

        # Here something went wrong
        print(u'{0} Revoke publication task failed'.format(request.id))
        revoke_publish_callback(unicode(error), None)
        raise
