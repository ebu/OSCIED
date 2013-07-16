#!/usr/bin/env python2
# -*- coding: utf-8 -*-

#**************************************************************************************************#
#              OPEN-SOURCE CLOUD INFRASTRUCTURE FOR ENCODING AND DISTRIBUTION : PUBLISHER
#
#  Authors   : David Fischer
#  Contact   : david.fischer.ch@gmail.com / david.fischer@hesge.ch
#  Project   : OSCIED (OS Cloud Infrastructure for Encoding and Distribution)
#  Copyright : 2012-2013 OSCIED Team. All rights reserved.
#**************************************************************************************************#
#
# This file is part of EBU/UER OSCIED Project.
#
# This project is free software: you can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This project is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
# even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this project.
# If not, see <http://www.gnu.org/licenses/>
#
# Retrieved from https://github.com/EBU-TI/OSCIED

import os
from celery import current_task
from celery.decorators import task
from Callback import Callback
from Media import Media
from PublisherConfig import PublisherConfig
from User import User
from pyutils.filesystem import recursive_copy
from pyutils.pyutils import object2json


@task(name='Publisher.publish_job')
def publish_job(user_json, media_json, callback_json):

    def copy_callback(start_date, elapsed_time, eta_time, src_size, dst_size, ratio):
        publish_job.update_state(state='PROGRESS', meta={
            'hostname': request.hostname, 'start_date': start_date, 'elapsed_time': elapsed_time,
            'eta_time': eta_time, 'media_size': src_size, 'publish_size': dst_size,
            'percent': int(100 * ratio)})

    def publish_callback(status, publish_uri):
        data = {'job_id': request.id, 'status': status}
        if publish_uri:
            data['publish_uri'] = publish_uri
        data_json = object2json(data, False)
        if callback is None:
            print('%s [ERROR] Unable to callback orchestrator: %s' % (request.id, data_json))
        else:
            r = callback.post(data_json)
            print('%s Code %s %s : %s' % (request.id, r.status_code, r.reason, r._content))

    # ----------------------------------------------------------------------------------------------

    RATIO_DELTA = 0.01  # Update status if at least 1% of progress
    TIME_DELTA = 1      # Update status if at least 1 second(s) elapsed

    try:
        # Avoid 'referenced before assignment'
        callback = None
        request = current_task.request

        # Let's the task begin !
        print('%s Publish job started' % (request.id))

        # Read current configuration to translate files uri to local paths
        config = PublisherConfig.read('local_config.pkl')
        print object2json(config, True)

        # Load and check task parameters
        user = User.load(user_json)
        media = Media.load(media_json)
        callback = Callback.load(callback_json)
        user.is_valid(True)
        media.is_valid(True)
        callback.is_valid(True)

        # Update callback socket according to configuration
        if config.api_nat_socket and len(config.api_nat_socket) > 0:
            callback.replace_netloc(config.api_nat_socket)

        # Verify that media file can be accessed
        media_path = config.storage_medias_path(media, generate=False)
        if not media_path:
            raise NotImplementedError('Media will not be readed from shared storage : %s' %
                                      media.uri)
        publish_path, publish_uri = config.publish_point(media)
        media_root, publish_root = os.path.dirname(media_path), os.path.dirname(publish_path)

        infos = recursive_copy(media_root, publish_root, copy_callback, RATIO_DELTA, TIME_DELTA)

        # Here all seem okay
        print('%s Publish job successful' % request.id)
        print('%s Callback : Media published as %s' % (request.id, publish_uri))
        publish_callback('SUCCESS', publish_uri)
        return {'hostname': request.hostname, 'start_date': infos['start_date'],
                'elapsed_time': infos['elapsed_time'], 'eta_time': 0,
                'media_size': infos['src_size'], 'publish_size': infos['src_size'], 'percent': 100}

    except Exception as error:

        # Here something went wrong
        print('%s Publish job failed ' % request.id)
        print('%s Callback : Something went wrong' % request.id)
        publish_callback(str(error), None)
        raise
