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

from __future__ import absolute_import, division, print_function, unicode_literals

import shutil, time
from celery import current_task
from celery.decorators import task
from os.path import dirname
from pytoolbox.datetime import datetime_now
from pytoolbox.encoding import configure_unicode, to_bytes
from pytoolbox.filesystem import recursive_copy
from pytoolbox.serialization import object2json
from pytoolbox.validation import valid_uri

from .config import PublisherLocalConfig
from .constants import LOCAL_CONFIG_FILENAME
from .models import Media, PublisherTask
from .utils import Callback


configure_unicode()

@task(name=u'PublisherWorker.publisher_task')
def publisher_task(media_json, callback_json):

    def copy_callback(start_date, elapsed_time, eta_time, src_size, dst_size, ratio):
        publisher_task.update_state(state=PublisherTask.PROGRESS, meta={
            u'hostname': request.hostname, u'start_date': start_date, u'elapsed_time': elapsed_time,
            u'eta_time': eta_time, u'media_size': src_size, u'publish_size': dst_size, u'percent': int(100 * ratio)})

    def publish_callback(status, publish_uri):
        data = {u'task_id': request.id, u'status': status}
        if publish_uri:
            data[u'publish_uri'] = publish_uri
        data_json = object2json(data, include_properties=False)
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

        # Read current configuration to translate files URIs to local paths
        local_config = PublisherLocalConfig.read(LOCAL_CONFIG_FILENAME, inspect_constructor=False)
        print(object2json(local_config, include_properties=True))

        # Load and check task parameters
        callback = Callback.from_json(callback_json, inspect_constructor=True)
        callback.is_valid(True)

        # Update callback socket according to configuration
        if local_config.api_nat_socket and len(local_config.api_nat_socket) > 0:
            callback.replace_netloc(local_config.api_nat_socket)

        media = Media.from_json(media_json, inspect_constructor=True)
        media.is_valid(True)

        # Verify that media file can be accessed
        media_path = local_config.storage_medias_path(media, generate=False)
        if not media_path:
            raise NotImplementedError(to_bytes(u'Media asset will not be readed from shared storage : {0}'.format(
                                      media.uri)))
        publish_path, publish_uri = local_config.publish_point(media)
        media_root, publish_root = dirname(media_path), dirname(publish_path)

        if not valid_uri(publish_uri, check_404=True):
            raise IOError(to_bytes(u'Media asset is unreachable from publication URI {0}'.format(publish_uri)))
        infos = recursive_copy(media_root, publish_root, copy_callback, RATIO_DELTA, TIME_DELTA)

        # Here all seem okay
        print(u'{0} Publication task successful, media asset published as {1}'.format(request.id, publish_uri))
        publish_callback(PublisherTask.SUCCESS, publish_uri)
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

@task(name=u'PublisherWorker.revoke_publisher_task')
def revoke_publisher_task(publish_uri, callback_json):

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

        # Read current configuration to translate files URIs to local paths
        local_config = PublisherLocalConfig.read(LOCAL_CONFIG_FILENAME, inspect_constructor=False)
        print(object2json(local_config, True))

        # Load and check task parameters
        callback = Callback.from_json(callback_json, inspect_constructor=True)
        callback.is_valid(True)

        # Update callback socket according to configuration
        if local_config.api_nat_socket and len(local_config.api_nat_socket) > 0:
            callback.replace_netloc(local_config.api_nat_socket)

        publish_root = dirname(local_config.publish_uri_to_path(publish_uri))
        if not publish_root:
            raise ValueError(to_bytes(u'Media asset is not hosted on this publication point.'))

        # Remove publication directory
        start_date, start_time = datetime_now(), time.time()
        shutil.rmtree(publish_root, ignore_errors=True)
        if valid_uri(publish_uri, check_404=True):
            raise IOError(to_bytes(u'Media asset is reachable from publication URI {0}'.format(publish_uri)))
        elapsed_time = time.time() - start_time

        # Here all seem okay
        print(u'{0} Revoke publication task successful, media asset unpublished from {1}'.format(
              request.id, publish_uri))
        revoke_publish_callback(PublisherTask.SUCCESS, publish_uri)
        return {u'hostname': request.hostname, u'start_date': start_date, u'elapsed_time': elapsed_time, u'eta_time': 0,
                u'percent': 100}

    except Exception as error:

        # Here something went wrong
        print(u'{0} Revoke publication task failed'.format(request.id))
        revoke_publish_callback(unicode(error), None)
        raise
