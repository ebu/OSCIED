#!/usr/bin/env python2
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

import os
from celery import current_task
from celery.decorators import task
from Callback import Callback
from Media import Media
from PublisherConfig import PublisherConfig
from User import User
from pyutils.py_filesystem import recursive_copy
from pyutils.py_serialization import object2json


@task(name=u'Publisher.publish_task')
def publish_task(user_json, media_json, callback_json):

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

    try:
        # Avoid 'referenced before assignment'
        callback = None
        request = current_task.request

        # Let's the task begin !
        print(u'{0} Publish task started'.format(request.id))

        # Read current configuration to translate files uri to local paths
        config = PublisherConfig.read(u'local_config.pkl')
        print object2json(config, True)

        # Load and check task parameters
        user = User.from_json(user_json)
        media = Media.from_json(media_json)
        callback = Callback.from_json(callback_json)
        user.is_valid(True)
        media.is_valid(True)
        callback.is_valid(True)

        # Update callback socket according to configuration
        if config.api_nat_socket and len(config.api_nat_socket) > 0:
            callback.replace_netloc(config.api_nat_socket)

        # Verify that media file can be accessed
        media_path = config.storage_medias_path(media, generate=False)
        if not media_path:
            raise NotImplementedError(u'Media will not be readed from shared storage : {0}'.format(media.uri))
        publish_path, publish_uri = config.publish_point(media)
        media_root, publish_root = os.path.dirname(media_path), os.path.dirname(publish_path)

        infos = recursive_copy(media_root, publish_root, copy_callback, RATIO_DELTA, TIME_DELTA)

        # Here all seem okay
        print(u'{0} Publish task successful, media published as {1}'.format(request.id, publish_uri))
        publish_callback(u'SUCCESS', publish_uri)
        return {u'hostname': request.hostname, u'start_date': infos[u'start_date'],
                u'elapsed_time': infos[u'elapsed_time'], u'eta_time': 0, u'media_size': infos[u'src_size'],
                u'publish_size': infos[u'src_size'], u'percent': 100}

    except Exception as error:

        # Here something went wrong
        print(u'{0} Publish task failed'.format(request.id))
        publish_callback(str(error), None)
        raise
